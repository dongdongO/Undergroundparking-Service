import cv2
import time

cap = cv2.VideoCapture('CCTV17_crop_2.mp4')

if not cap.isOpened():
    print('Video open failed!')


# 트래커 객체 생성

# Kernelized Correlation Filters : 빠름 But 정확도 약간 낮음
tracker = cv2.TrackerKCF_create()

# Minimum Output Sum of Squared Error : 굉장히 빠름 But 정확도 낮음
#tracker = cv2.legacy.TrackerMOSSE_create()

# Discriminative Correlation Filter with Channel and Spatial Reliability # 느려서 안될듯
#tracker = cv2.TrackerCSRT_create()

# 첫 번째 프레임에서 추적 ROI 설정
ret, frame = cap.read()

if not ret:
    print('Frame read failed!')

# frame 이라는 이름으로 부분영상 추출
rc = cv2.selectROI('frame', frame)

# 초깃값 설정
tracker.init(frame, rc)

#__init__
time_cost = 0
fps_cost = 0
frame_num = 0


# 매 프레임 처리
while True:
    ret, frame = cap.read()
    start = time.time()
    frame_num +=1 

    if not ret:
        print('Frame read failed!')
        break
    
    # 추척 $ ROI 사각형 업데이트
    # 매 프래임마다 update하고 rc값 받아옴
    ret, rc = tracker.update(frame)
    
    # floate 형태로 rc값을 받으므로 int로 변환해서 list로 감싸고 tuple로 변환
    rc = list([int(_) for _ in rc])
    cv2.rectangle(frame, rc, (0, 0, 255), 2)
    
    time_temp = 1000*(time.time()-start)  
    if time.time()-start != 0.0:
        fps_temp = 1/(time.time()-start)  
    else:
        fps_temp=0.01
    
    time_cost = time_cost + time_temp
    fps_cost = fps_cost + fps_temp
    
    cv2.imshow('frame', frame)
    if cv2.waitKey(20) == 27:
        break

print('소요시간 평균 : {:.2f} ms\t 평균FPS : {:.2f}'.format(time_cost / frame_num, fps_cost/ frame_num))
cap.release()
cv2.destroyAllWindows()

