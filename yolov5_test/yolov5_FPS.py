import cv2
import torch
import time

yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s',
                            device='cuda:0' if torch.cuda.is_available() else 'cpu')  # 예측 모델
yolo_model.classes = [2]  # 예측 클래스 (사람)

cap = cv2.VideoCapture('/home/dongdong/yolov5_sort/CCTV17_crop_1.mp4')

#__init__
time_cost = 0
fps_cost = 0
frame_num = 0

while True:
    start = time.time()
    frame_num +=1 
    ret, frame = cap.read()
    
    if frame is None:
        break
    
    results = yolo_model(frame)
    results_refine = results.pandas().xyxy[0].values
    nms_human = len(results_refine)
    if nms_human > 0:
        for bbox in results_refine:
            start_point = (int(bbox[0]), int(bbox[1]))
            end_point = (int(bbox[2]), int(bbox[3]))

            frame = cv2.rectangle(frame, start_point, end_point, (255, 0, 0), 3)
            
    time_temp = 1000*(time.time()-start)  
    if time.time()-start != 0.0:
        fps_temp = 1/(time.time()-start)  
    else:
        fps_temp=0.01
    
    time_cost = time_cost + time_temp
    fps_cost = fps_cost + fps_temp
    
    cv2.imshow("Video streaaming", frame)
    if cv2.waitKey(1) == ord("q"):
        break

print('소요시간 평균 : {:.2f} ms\t 평균FPS : {:.2f}'.format(time_cost / frame_num, fps_cost/ frame_num))
cap.release()
cv2.destroyAllWindows()