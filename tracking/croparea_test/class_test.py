import cv2
import time
from kalmanFilter import *
from framecrop import *
from MovingTracking import MovingTracking
import cProfile

video_capture = cv2.VideoCapture("/mnt/c/Users/tom41/OneDrive/Desktop/dataset_videos/double_cars1.mp4")

video_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
video_fps = int(video_capture.get(cv2.CAP_PROP_FPS))

#init
Green = (0,255,0)
Red = (0,0,255)
Blue = (255,0,0)
Pink = (255,0,255)

"""
point = [
    [(259, 220), (653, 220),(617, 535), (121, 535)],
    [(780, 215), (996, 215), (1226, 500), (950, 500)],
    [(644, 92), (887, 88), (932, 183), (629, 178)],
]
"""

point = [
    [(0, 190), (1280, 190), (1280, 720), (0, 720)],
    [(0,0), (1280, 0), (1280, 190), (0, 190)],
]
trackers = []
output_results = []

for i in range(len(point)):
    trackers.append(MovingTracking())
    output_results.append(None)

previous_frame = None

time_cost = 0
time_check =0
fps_cost = 0
frame_num = 0

while True:
    input_key = cv2.waitKey(video_fps) 
    start = time.time()
    frame_num += 1

    #ESC to quit
    if input_key == 27:
        break
    
    #time.sleep(1)
    return_value, frame = video_capture.read()

    if return_value:
        pass
    else : 
        print('The video ended or an error occurred')
        break
    
    # erase timer above
    cv2.rectangle(frame, (100,10), (600,60), (0,0,0), thickness=-1)

    # 1. preprocessing the frame; Grayscale & Blur
    prepared_frame = image_preprocessing(frame)
    
    # update previous_frame if None
    if (previous_frame is None):
        previous_frame = prepared_frame
        continue

    # 2. extract contours from preprocessed frame & update previous frame
    dilate_frame = frame_preprocessing(previous_frame, prepared_frame)
    previous_frame = prepared_frame
    
    # 3. combine contours; greedy_box, ratio_box, contour_itself 
    frame_output_use, frame_output = frame_crop(frame, dilate_frame, point)

    for i, tracker in enumerate(trackers):
        output_results[i] = tracker.detect_motion(frame_output_use[i], frame_output[i])
    
    time_temp = 1000*(time.time()-start)  
    if time.time()-start != 0.0:
        fps_temp = 1/(time.time()-start)  
    else:
        fps_temp=0.01

    time_check += time_temp
    time_cost = time_cost + time_temp
    fps_cost = fps_cost + fps_temp
    
    # 9. Show the result
    for i, output_result in enumerate(output_results):
        cv2.imshow(f"result{i+1}", output_result)
    
# 10. Memory return
print('소요시간 평균 : {:.2f} ms\t 평균FPS : {:.2f}'.format(time_cost / frame_num, fps_cost/ frame_num))
video_capture.release()
cv2.destroyAllWindows()