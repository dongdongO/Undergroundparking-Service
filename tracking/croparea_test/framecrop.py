import cv2
import numpy as np
from math import dist

# Preprocessing; Grayscale & Blur
def image_preprocessing(frame):
    frame_GRAY = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
    frame_Blur = cv2.GaussianBlur(src=frame_GRAY, ksize=(5,5), sigmaX=0)
    
    return frame_Blur

# Calculate difference frame & contours; return contours
def frame_preprocessing(previous_frame, frame):
    # 1. Calculate difference and update previous frame
    diff_frame = cv2.absdiff(src1=previous_frame, src2=frame)

    # 2. Dilute the image to make differences more seeable; more suitable for contour detection
    kernel = np.ones((3, 3))
    dilate_frame = cv2.dilate(src=diff_frame, kernel=kernel, iterations=1)

    return dilate_frame

def frame_crop(frame_org, frame_dilate, point_lst):
    result_frame_dilate = []
    result_frame_org = []
    
    for _, point in enumerate(point_lst):
        pts = np.array([point[0], point[1], point[2], point[3]], np.int32)
        # Reshape the array into a 2D array
        pts = pts.reshape((-1, 1, 2))

        # Create a mask for the region of interest
        mask_dilate = np.zeros_like(frame_dilate)
        cv2.fillPoly(mask_dilate, [pts], (255, 255, 255))
        
        mask_org = np.zeros_like(frame_org)
        cv2.fillPoly(mask_org, [pts], (255, 255, 255))

        # Apply the mask to the input image
        masked_img_dilate = cv2.bitwise_and(frame_dilate, mask_dilate)
        masked_img_org = cv2.bitwise_and(frame_org, mask_org)

        # Get the coordinates of the bounding box of the masked image
        (x, y, w, h) = cv2.boundingRect(pts)

        # Crop the masked image to the size of the bounding box
        result_frame_dilate.append(masked_img_dilate[y:y+h, x:x+w])
        result_frame_org.append(masked_img_org[y:y+h, x:x+w])

    return result_frame_dilate, result_frame_org


def combine_contour(contours, MinArea):
    cnts_conditionpass=[]
    result = []
    
    for _, cnt_value in enumerate(contours):
        # smaller than MinArea; pass
        # calculate centerpoint and area each
        area = cv2.contourArea(cnt_value)
        if area > MinArea:
            M = cv2.moments(cnt_value)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cnts_conditionpass.append([cX,cY,area])
            
    count = len(cnts_conditionpass)
    if count == 0 or count == 1:
        return cnts_conditionpass
    # until all contours merge
    else:
        zone1 = cnts_conditionpass[0]
        for i in range(1, count):
            tmpZones = merge_contour(zone1, cnts_conditionpass[i])
            zone1 = tmpZones

    result.append([int(tmpZones[0]), int(tmpZones[1])])
    
    return result


def merge_contour(z1, z2):
    sum_area = z1[2] + z2[2]
    
    center_X = int(z1[0]*(z1[2]/sum_area) + z2[0]*(z2[2]/sum_area))
    center_Y = int(z1[1]*(z1[2]/sum_area) + z2[1]*(z2[2]/sum_area))
    
    return [center_X, center_Y, sum_area]

def frame_crop_test(frame_org, frame_dilate, point_lst):
    # Combine all points into a single numpy array and reshape it into a 3D array
    pts = np.array(point_lst, np.int32)
    pts = pts.reshape((-1, 1, 2))

    # Create a mask for the region of interest
    mask_dilate = np.zeros_like(frame_dilate)
    cv2.fillPoly(mask_dilate, [pts], (255, 255, 255))
    
    mask_org = np.zeros_like(frame_org)
    cv2.fillPoly(mask_org, [pts], (255, 255, 255))

    # Apply the mask to the input images
    masked_img_dilate = cv2.bitwise_and(frame_dilate, mask_dilate)
    masked_img_org = cv2.bitwise_and(frame_org, mask_org)

    # Get the dimensions of the bounding box of the masked image
    (x, y, w, h) = cv2.boundingRect(pts)

    # Allocate numpy arrays of the correct size for the cropped images
    result_frame_dilate = np.zeros((len(point_lst), h, w), dtype=np.uint8)
    result_frame_org = np.zeros((len(point_lst), h, w), dtype=np.uint8)

    # Iterate over the points and crop the images
    for i, pts in enumerate(pts):
        result_frame_dilate[i] = masked_img_dilate[y:y+h, x:x+w]
        result_frame_org[i] = masked_img_org[y:y+h, x:x+w]

    return result_frame_dilate, result_frame_org