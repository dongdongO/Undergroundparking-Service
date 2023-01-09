import cv2
import numpy as np
import time

capture = cv2.VideoCapture('./CCTV17_crop_4.mp4')

width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

bget_KNN = cv2.createBackgroundSubtractorKNN(detectShadows=False)
bget_MOG2 = cv2.createBackgroundSubtractorMOG2(history=200,varThreshold=32,detectShadows=False)

#kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))

while cv2.waitKey(33) < 0:
    start = time.time()
    
    return_value, frame = capture.read()
    # 비디오 프레임 정보가 있으면 계속 진행 
    if return_value:
        pass
    else : 
        print('비디오가 끝났거나 오류가 있습니다')
        break
    
    backgroundsub_mask_MOG2 = bget_MOG2.apply(frame)
    backgroundsub_mask_MOG2 = cv2.morphologyEx(backgroundsub_mask_MOG2,cv2.MORPH_CLOSE, kernel)
    #backgroundsub_mask_MOG2 = cv2.dilate(backgroundsub_mask_MOG2,kernel,iterations=1)
    backgroundsub_mask_MOG2 = np.stack((backgroundsub_mask_MOG2,)*3, axis=-1)
    
    
    backgroundsub_mask_KNN = bget_KNN.apply(frame)
    backgroundsub_mask_KNN = cv2.morphologyEx(backgroundsub_mask_KNN,cv2.MORPH_CLOSE, kernel)
    #backgroundsub_mask_KNN = cv2.dilate(backgroundsub_mask_KNN,kernel,iterations=1)
    backgroundsub_mask_KNN = np.stack((backgroundsub_mask_KNN,)*3, axis=-1)

    #cv2.imshow('backgroundsub_MOG2', backgroundsub_mask_MOG2)
    cv2.imshow('backgroundsub_KNN', backgroundsub_mask_KNN)
        
    cv2.imshow('original', frame)
    
capture.release()
cv2.destroyAllWindows()   

