import cv2
import numpy as np

# calculate difference frame & contours; return contours
def frame2contour(previous_frame, frame):
    """이전 grayscale된 frame과 현재 grayscale된 frame의 차영상을 구하고 contour를 뽑아내는 함수
    Args :
        previous_frame  (ndarray): 이전 grayscale된 frame
        frame           (ndarray): 현재 grayscale된 frame
        
    Returns:
        contours          (tuple): 추출된 모든 contour
    """
    # 1. Calculate difference and update previous frame
    diff_frame = cv2.absdiff(src1=previous_frame, src2=frame)
    # cv2.imshow('preprocessed video', diff_frame)
    
    # 2. Blur substracted frame
    blur_frame = cv2.GaussianBlur(src=diff_frame, ksize=(7,7), sigmaX=0)
    cv2.imshow('blur video', blur_frame)
    
    # 3. Dilate the image to make differences more seeable; more suitable for contour detection
    kernel = np.ones((9, 9))
    dilate_frame = cv2.dilate(src=blur_frame, kernel=kernel, iterations=1)
    # cv2.imshow('preprocessed video', dilate_frame)

    # 4. Only take different areas that are different enough (over 30: draw white); calculate degree of difference
    _, threshold_frame = cv2.threshold(src=dilate_frame, thresh=50, maxval=255, type=cv2.THRESH_BINARY)
    # cv2.imshow('threshold video', threshold_frame)
    
    # 5. Find contours after thresholding
    contours, _ = cv2.findContours(image=threshold_frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

    return contours