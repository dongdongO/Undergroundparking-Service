import cv2
import time

capture = cv2.VideoCapture("/mnt/c/Users/tom41/OneDrive/Desktop/dataset_videos/parking1.mp4")

time_cost = 0
time_check =0
fps_cost = 0
frame_num = 0
video_fps = int(capture.get(cv2.CAP_PROP_FPS))
capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
count = 0


# get the number of frames in the video buffer
num_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

# print the number of frames
print("Number of frames in video buffer: ", num_frames)

while True:
    key = cv2.waitKey(1)
    start = time.time()
    if key == 27:
        break

    if frame_num % 5 == 0:
        return_value, frame = capture.read()
    
    if return_value:
        pass
    else:
        print('The video ended or an error occured')
        break
    frame_num += 1
    # for i in range(0, video_fps-1):
    #     capture.grab()
    #     frame_num += 1
    
    # if capture.grab():
    #     success, img = capture.retrieve()
    #     if success:
    #         frame_num += 1
    #         captured_frame = img
    #         cv2.putText(captured_frame, 'Frame number : '+ str(frame_num), (40, 530), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))
    #         cv2.imwrite('./result_' + str(i) + '.jpg', captured_frame)
    # else:
    #     pass
    
    #소요 시간 및 평균 FPS 구하기
    time_temp = 1000*(time.time()-start)  
    if time.time()-start != 0.0:
        fps_temp = 1/(time.time()-start)  
    else:
        fps_temp=0.01

    time_check += time_temp
    time_cost = time_cost + time_temp
    fps_cost = fps_cost + fps_temp
    
    cv2.imshow('result', frame)
    #cv2.imshow('result', captured_frame)

print('소요시간 평균 : {:.2f} ms\t 평균FPS : {:.2f}'.format(time_cost / frame_num, fps_cost/ frame_num))
print(f"총 frame : {frame_num}")
capture.release()
cv2.destroyAllWindows()
