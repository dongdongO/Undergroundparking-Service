import cv2
import time
import numpy as np
#from test import eliminate_light, get_RBG_in_image

def gray2hsv(gray):
    assert len(gray.shape) == 2
    height, width = gray.shape
    gray = np.expand_dims(gray, axis=2)
    img = np.zeros((height, width, 2), dtype=np.uint8)
    img = np.append(img, gray, axis=2)
    return img
    
    
#불러올 영상 & 녹화할 영상 위치
capture = cv2.VideoCapture("./dataset_videos/CCTV17.mp4")
output_path = './dataset_videos/output_result.mp4'


#불러온 영상의 가로,세로,fps & 녹화할 영상 저장 형식
width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(capture.get(cv2.CAP_PROP_FPS))
codec = cv2.VideoWriter_fourcc(*'mp4v')

#init
time_cost = 0
fps_cost = 0
frame_num = 0


# 영상 frame 별로 처리
while True:
    key = cv2.waitKey(33)
    start = time.time()
    
    #ESC 누르면 종료됨
    if key == 27:
        break
    
    return_value, frame = capture.read()
    # 비디오 프레임 정보가 있으면 계속 진행 
    if return_value:
        pass
    else : 
        print('비디오가 끝났거나 오류가 있습니다')
        break

    #frame = eliminate_light(frame)
    
    origin_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    origin_image = gray2hsv(origin_image)
    origin_image = cv2.blur(origin_image, (5, 5), anchor=(-1, -1), borderType=cv2.BORDER_DEFAULT)
    
    mask = cv2.inRange(origin_image, (0,0,90),(180,30,230))
    mask = np.stack((mask,)*3, axis=-1)
    
    mask = cv2.bitwise_not(mask)
    
    origin_test = cv2.bitwise_and(mask, frame)
    
    canny = cv2.Canny(origin_test, 100, 255)
    canny = np.stack((canny,)*3, axis=-1)

    #소요 시간 및 평균 FPS 구하기
    time_temp = 1000*(time.time()-start)  
    if time.time()-start != 0.0:
        fps_temp = 1/(time.time()-start)  
    else:
        fps_temp=0.01

    time_cost = time_cost + time_temp
    fps_cost = fps_cost + fps_temp
    #print('소요 시간 : {:.2f} ms \t 평균FPS : {:.2f}'.format(time_temp,fps_temp))
    
    #param = {'image' : origin_image}
    
    concat_image_process = np.concatenate((origin_image, mask), axis=1)
    cv2.imshow('process', concat_image_process)
    
    concat_image_test = np.concatenate((origin_test, canny), axis=1)
    cv2.imshow('result',concat_image_test)
    #cv2.setMouseCallback('image', get_RBG_in_image, param)

    

#메모리 반납
print('소요시간 평균 : {:.2f} ms\t 평균FPS : {:.2f}'.format(time_cost / frame_num, fps_cost/ frame_num))
capture.release()
cv2.destroyAllWindows()