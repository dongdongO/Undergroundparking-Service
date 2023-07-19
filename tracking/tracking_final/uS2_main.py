import cv2
import time
import numpy as np
from kalmanFilter import kalmanFilter_
from frame2contour import frame2contour
from sort import Sort
from combine_zone import combine_contour
from update_ID import update_ID

video_capture = cv2.VideoCapture("/mnt/c/Users/tom41/OneDrive/Desktop/dataset_videos/double_cars1.mp4")

video_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
video_fps = int(video_capture.get(cv2.CAP_PROP_FPS))

# init
Green = (0,255,0)
Red = (0,0,255)
Blue = (255,0,0)
Pink = (255,0,255)

time_cost = 0
fps_cost = 0
frame_num = 0

previous_frame = None

MinArea = 200
threshold = 350

mot_tracker = Sort()
track_bbs_ids = None
detections = np.empty((0, 5))

update_count = []
tracking_input = []
tracking_Kfilter = []
P = []

while True:
    input_key = cv2.waitKey(0) 
    start = time.time()
    frame_num += 1

    #ESC to quit
    if input_key == 27:
        break
    
    return_value, frame = video_capture.read()

    if return_value:
        pass
    else : 
        print('The video ended or an error occurred')
        break
    
    # If no input
    if len(detections) == 0:
        detections = np.empty((0, 5))
    
    # 1. Update tracking
    track_bbs_ids = mot_tracker.update(detections) 
    
    # Erase timer above
    cv2.rectangle(frame, (100,10), (600,60), (0,0,0), thickness=-1)
    #cv2.rectangle(frame, (1450,40), (1850,100), (0,0,0), thickness=-1)
    #cv2.rectangle(frame, (15, 20), (170, 40), (0,0,0), thickness=-1)
    
    # 2. Grayscale the image and save it for the next loop
    frame_gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
    prepared_frame = frame_gray
    
    # Update previous_frame if None : skip the rest
    if (previous_frame is None):
        previous_frame = prepared_frame
        continue

    # 3. Extract contours from preprocessed frame & update previous frame
    contour = frame2contour(previous_frame, prepared_frame)
    previous_frame = prepared_frame
    
    # cv2.drawContours(frame, contour, -1, Pink,2, cv2.LINE_AA)
    
    # 4. Combine contours; greedy_box, ratio_box, contour_itself 
    combined_center = combine_contour(contour, MinArea,threshold)
    
    # Draw inputs : red
    for _, live_p in enumerate(combined_center):
        cv2.circle(frame, (live_p[0], live_p[1]), 10, Red, -1)

    # 5. Update tracking info
    tracking_input, tracking_Kfilter, P, update_count = update_ID(combined_center, tracking_input, tracking_Kfilter, P, update_count)

    # 6. Update tracking_Kfilter, P : filtered input
    for j, filtered_p in enumerate(tracking_input):
        z_meas = np.array([filtered_p[0],filtered_p[1]])
        tracking_Kfilter[j], P[j] = kalmanFilter_(z_meas, tracking_Kfilter[j], P[j])
    
    # 7. Save the result for tracking : update by next frame
    detections = []
    for i,coordinate in enumerate(tracking_Kfilter):
        detection = [coordinate[0]-80, coordinate[2]-80, coordinate[0]+80, coordinate[2]+80]
        detections.append(detection)
        cv2.circle(frame, (int(coordinate[0]),int(coordinate[2])), 10, Green, -1)
    detections = np.array(detections)
    
    # Draw tracking : Blue box
    if track_bbs_ids is not None:
        for bbox in track_bbs_ids:
            start_point = (int(bbox[0]), int(bbox[1]))
            end_point = (int(bbox[2]), int(bbox[3]))
            name_idx = int(bbox[4])
            name = "ID : {}".format(str(name_idx))
            cv2.rectangle(frame, start_point, end_point, Blue, 3)
            cv2.putText(frame, name, start_point, cv2.FONT_HERSHEY_SIMPLEX, 0.9, Green,3)

    # Calculate time spend
    time_temp = 1000*(time.time()-start)  
    if time.time()-start != 0.0:
        fps_temp = 1/(time.time()-start)  
    else:
        fps_temp=0.01

    time_cost = time_cost + time_temp
    fps_cost = fps_cost + fps_temp
    
    # 8. Show the result
    cv2.imshow('result', frame)
    
# 9. Memory return
print('소요시간 평균 : {:.2f} ms'.format(time_cost / frame_num))
video_capture.release()
cv2.destroyAllWindows()
