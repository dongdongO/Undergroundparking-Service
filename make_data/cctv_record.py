# import modules
import cv2
import time

# rtsp address
source = "rtsp://admin:123456@172.10.14.28/media/video2"
cap = cv2.VideoCapture(source)

# set codec to MJPG
fourcc = cv2.VideoWriter_fourcc(*'MJPG')

# get width, height, fps
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# save video : VideoWriter(name, codec, fps, (width, hegiht))
out = cv2.VideoWriter('TestVideo.mp4', fourcc, 30, (width, height))

# current time + 10 sec
max_time = time.time() + (10)

while True:
    ret, frame = cap.read()
    
    if not ret:
        break

    cv2.imshow('video', frame)
    out.write(frame)

    k = cv2.waitKey(1)
    
    # exit : ESC
    if(k==27):
        break

    if time.time() > max_time:
        break

# return memory
cap.release()
out.release()
cv2.destroyAllWindows()