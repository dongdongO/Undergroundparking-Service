import cv2
import time
import numpy as np


#불러올 영상 & 녹화할 영상 위치
capture = cv2.VideoCapture("./CCTV17_crop_2.mp4")
output_path = './output_result.mp4'

#불러온 영상의 가로,세로,fps & 녹화할 영상 저장 형식
width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(capture.get(cv2.CAP_PROP_FPS))
codec = cv2.VideoWriter_fourcc(*'mp4v')

# 배경 추출을 위한 KNN,kernel 설정
bget_KNN = cv2.createBackgroundSubtractorKNN(detectShadows=False)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))

#init
time_cost = 0
fps_cost = 0
frame_num = 0
check = 0
record = False

# 영상 frame 별로 처리
while True:
    key = cv2.waitKey(33)
    start = time.time()
    frame_num +=1 
    
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

    origin_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    origin_image = cv2.blur(origin_image, (3, 3), anchor=(-1, -1), borderType=cv2.BORDER_DEFAULT)
    
    mask = cv2.inRange(origin_image, (0,0,90),(180,30,230))
    range_image = cv2.bitwise_and(origin_image, origin_image, mask=mask)
    mask = np.stack((mask,)*3, axis=-1)
    
    mask = cv2.bitwise_not(mask)
    
    origin_test = cv2.bitwise_and(mask, frame)

    #소요 시간 및 평균 FPS 구하기
    time_temp = 1000*(time.time()-start)  
    if time.time()-start != 0.0:
        fps_temp = 1/(time.time()-start)  
    else:
        fps_temp=0.01

    time_cost = time_cost + time_temp
    fps_cost = fps_cost + fps_temp
    #print('소요 시간 : {:.2f} ms \t 평균FPS : {:.2f}'.format(time_temp,fps_temp))

    cv2.imshow('image', origin_image)
    cv2.imshow('test_mask', mask)
    cv2.imshow('test_range_image', origin_test)
    

#메모리 반납
print('소요시간 평균 : {:.2f} ms\t 평균FPS : {:.2f}'.format(time_cost / frame_num, fps_cost/ frame_num))
capture.release()
cv2.destroyAllWindows()