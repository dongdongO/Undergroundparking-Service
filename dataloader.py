import math
import time
from threading import Thread
import cv2
import numpy as np
import yaml
from utils.general import (LOGGER, check_requirements)

# Parameters
IMG_FORMATS = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']


class LoadData:
    """
    CPU 성능에 따라 다수의 CCTV 멀티쓰레드로 처리 시 리소스 할당 등의 문제로 예측속도가 느려지는 문제 발생
    CCTV 영상을 획득하는 VideoCapture 객체를 영상서버 하드웨어 성능에 따라 유동적으로 사용할 수 있도록 수정
    한 개의 VideoCapture 객체가 1개의 CCTV를 담당하는 방식에서 다수의 CCTV를 순차적으로 영상 획득하여 전달하는 방식으로 변경
                    
    """
    def __init__(self, mode, cams):
        self.__streams = {}
        self.__idx = 0
        self.__mode = mode
        self.__cams__ = cams
        self.__thread = True

        max_VideoCapture = 10 # 최대 비디오캡처 thread 수
        cctv_data = {}        # cctv 분할 정보 및 thread 할당
        for i in range(0, max_VideoCapture):
            cctv_data[i] = {}
            cctv_data[i]['src'] = []
            cctv_data[i]['cam_seq'] = []

        for i, cam_seq in enumerate(self.__cams__):
            cam = self.__cams__[cam_seq]
            source = cam['src']
            id = i % max_VideoCapture
            cctv_data[id]['src'].append(source)
            cctv_data[id]['cam_seq'].append(cam_seq)
            
            if cam_seq not in self.__streams:
                self.__streams[cam_seq] = {'frames': float('inf'), 'fps': 30, 'image': None}
            # try:     
            #     cap = cv2.VideoCapture(source)
            #     assert cap.isOpened()
            #     w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            #     h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            #     fps = cap.get(cv2.CAP_PROP_FPS)  # warning: may return 0 or na
            #     self.__streams[cam_seq]['frames'] = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 0) or float('inf')  # infinite stream fallback
            #     self.__streams[cam_seq]['fps'] = max((fps if math.isfinite(fps) else 0) % 100, 0) or 30  # 30 FPS fallback

            #     # 초기 연결 테스트
            #     def cam_read(count):
            #         __, self.__streams[cam_seq]['image'] = cap.read()  # guarantee first frame
            #         if self.__streams[cam_seq]['image'] is not None:
            #             count = 0
            #         else:
            #             count += 1
            #             cam_read(count)
            #         if count == 0:
            #             cap.release()
            #             return

            #     cam_read(0)
            #     LOGGER.info(f"{cam_seq} Success ({self.__streams[cam_seq]['frames']} frames {w}x{h} at {self.__streams[cam_seq]['fps']:.2f} FPS)")
 
            # except AssertionError as e:
            #     LOGGER.exception(e)
            # except RecursionError as e:
            #         LOGGER.exception(e)

        # 제한된 VideoCapture 스레드 생성
        for i in range(0, max_VideoCapture):
            cctv_data[i]['thread'] = Thread(target=self.__update, args=([i,cctv_data[i]['src'], cctv_data[i]['cam_seq']]), daemon=True)
            cctv_data[i]['thread'].start()
            self.__thread = True
            while (self.__thread):
                time.sleep(1)

    def __update(self, num, cctv_src, cctv_seq):
        cctv = {}
        for i in range(0, len(cctv_src)):
            err_count = 0
            while True:
                cctv[i] = cv2.VideoCapture(cctv_src[i])
                
                if cctv[i].isOpened():
                    w = int(cctv[i].get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(cctv[i].get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cctv[i].get(cv2.CAP_PROP_FPS) 
                    cctv[i].set(cv2.CAP_PROP_BUFFERSIZE, 1)
       
                    cam_seq = cctv_seq[i]
                    source = cctv_src[i]
                    self.__streams[cam_seq]['frames'] = max(int(cctv[i].get(cv2.CAP_PROP_FRAME_COUNT)), 0) or float('inf')  # infinite stream fallback
                    self.__streams[cam_seq]['fps'] = max((fps if math.isfinite(fps) else 0) % 100, 0) or 30  # 30 FPS fallback
                    
                    rst, frame = cctv[i].read()
                    if rst:
                        self.__streams[cam_seq]['image'] = frame
                        LOGGER.info(f"{cam_seq} Success ({self.__streams[cam_seq]['frames']} frames {w}x{h} at {self.__streams[cam_seq]['fps']:.2f} FPS)")
                        break
                    else:
                        err_count += 1
                        time.sleep(1 / self.__streams[cam_seq]['fps'])
                        
                else:
                    cctv[i].open(source)
                    err_count += 1
                if err_count > 100:
                    LOGGER.warning(f'{cam_seq} Connection Fail')
                    break
        self.__thread = False
        LOGGER.info(f'{num} CCTV Thread Connected')
            
        while True:
            for i in range(0, len(cctv_src)):
                err_count = 0
                while True:
                    cam_seq = cctv_seq[i]
                    source = cctv_src[i]
                    
                    for j in range(0, int(self.__streams[cam_seq]['fps']-1)):
                        cctv[i].grab()
    
                        
                    if cctv[i].grab():
                        success, im = cctv[i].retrieve()
                        if success:
                            self.__streams[cam_seq]['image'] = im
                            
                            #if i == 5:
                                #cv2.imwrite('/home/ves/CCTV_images/' + cam_seq + '.jpg', im)
                            
                            time.sleep(0.5)
                         
                            #LOGGER.info(f'{cam_seq} Image Update')
                            break
            
                        else:
                            LOGGER.warning('WARNING: Video stream unresponsive, please check your IP camera connection.')
                            self.__streams[cam_seq]['image'] = np.zeros_like(self.__streams[cam_seq]['image'])
                            cctv[i].open(source)  # re-open stream if signal was lost
                            err_count += 1
                    else:
                        cctv[i].open(source)
                        err_count += 1
                        
                    if err_count > 100:
                        LOGGER.warning(f'WARNINIG : {cam_seq} connection fail')
                        break
                    time.sleep(1 / self.__streams[cam_seq]['fps'])  # wait time

                
       

    def __iter__(self):
        return self

    def __next__(self):
        cam_seq = list(self.__cams__)[self.__idx]
        cam = self.__cams__[cam_seq]

        source = cam['src']
        is_img_file = source.lower().endswith(tuple(IMG_FORMATS))
        is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
        webcam = source.isnumeric() or source.endswith('.txt') or (is_url and not is_img_file)

        # if webcam:
        #     if not all(x.is_alive() for x in self.__streams[cam_seq]['thread']) or cv2.waitKey(1) == ord('q'):  # q to quit
        #         cv2.destroyAllWindows()
        #     raise StopIteration

        self.__idx += 1
        if self.__idx > len(list(self.__cams__)) - 1:
            self.__idx = 0

        return cam_seq, cam, self.__streams[cam_seq]['image'], None, webcam, ''

    def __len__(self):
        return len(list(self.__cams__))
