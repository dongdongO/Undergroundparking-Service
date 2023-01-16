import cv2
import torch
from sort import *
import numpy
import time

model = torch.hub.load('ultralytics/yolov5', 'yolov5m',
                            device='cuda:0' if torch.cuda.is_available() else 'cpu')
model.classes = [2] #자동차만
cap = cv2.VideoCapture('/mnt/c/Users/tom41/OneDrive/Desktop/dataset_videos/CCTV17.mp4')

mot_tracker = Sort()

#__init__
time_cost = 0
fps_cost = 0
frame_num = 0
yolo_frame_num = 0


while(True):
    start = time.time()
    frame_num +=1 
    ret, frame = cap.read()
    
    if frame is None:
        break
    
    #time.sleep(0.01)
    if frame_num%5==0:
        yolo_frame_num += 1
        preds = model(frame)
        detections = preds.pandas().xyxy[0].values
        track_bbs_ids = mot_tracker.update(detections)
        #update를 했을 때 변화가 있는 놈들은 ROI색을 달리 할 수 있을까?
        nms_car = len(detections)
        
        if nms_car > 0:
            for bbox in track_bbs_ids:
                start_point = (int(bbox[0]), int(bbox[1]))
                end_point = (int(bbox[2]), int(bbox[3]))
                name_idx = int(bbox[4])
                name = "ID : {}".format(str(name_idx))
                frame = cv2.rectangle(frame, start_point, end_point, (255, 0, 0), 3)
                frame = cv2.putText(frame, name, start_point, cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0),3)
    
        frame = cv2.putText(frame, 'FPS : '+str(int(fps_cost/frame_num)), (0,300),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2 )
        cv2.imshow('Image', frame)    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    time_temp = 1000*(time.time()-start)  
    if time.time()-start != 0.0:
        fps_temp = 1/(time.time()-start)  
    else:
        fps_temp=0.01
    
    time_cost = time_cost + time_temp
    fps_cost = fps_cost + fps_temp
    
    

print('소요시간 평균 : {:.2f} ms\t 평균FPS : {:.2f} ms'.format(time_cost / frame_num, fps_cost/ frame_num))
print('총 frame 개수 : {} 개\t\t 실제 frame 개수 : {} 개'.format(frame_num, yolo_frame_num))
cap.release()
cv2.destroyAllWindows()