#opencv 와 time 모듈 불러오기
import cv2
import time

#가져올 cctv rtsp 위치 (rtsp에 대한 대략적 정보 공부)
source = "rtsp://admin:123456@172.10.14.28/media/video2"
#그 위치에 있는 영상 재생 by cv2.VideoCapture
cap = cv2.VideoCapture(source)
#저장할 동영상의 '코덱' 설정
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
#동영상의 가로,세로,FPS 구하기  
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
#동영상 저장 방식 by VideoWriter('저장될이름', 코덱, fps, (가로,세로))
out = cv2.VideoWriter('TestVideo.mp4', fourcc, 30, (width, height))

# time.time()은 컴퓨터의 현재 시간
max_time = time.time() + (10)

#동영상을 불러 오는 기본 꼴
while True:
    ret, frame = cap.read()
    
    if not ret:
        break

    cv2.imshow('video', frame)
		#이부분으로 cctv의 영상을 out에다가 저장
    out.write(frame)

		#waitKey 안에 있는 수로 영상의 속도 조절 가능
    k = cv2.waitKey(1)
    if(k==27):
        break

    if time.time() > max_time:
        break
#메모리 반환 필수!!
cap.release()
out.release()
cv2.destroyAllWindows()