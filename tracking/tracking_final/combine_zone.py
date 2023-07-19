import cv2
import numpy as np
from math import dist

def combine_contour(contours, MinArea, threshold):
    """일정 거리 내의 모든 contour들의 중심점 구하기
    Args :
        contours       (tuple): cv2.findContours를 통해 구한 모든 contour 집합
        MinArea          (int): 이 값 이상의 contour만 남기기
        threshold        (int): 이 값 이하의 거리를 가진 contour의 중점을 합치기
    
    Returns :
        merge_center (ndarray): 합쳐진 중점들의 좌표 (예: [[x1, y1], [x2, y2]])
    """
    cnts_conditionpass=[]
    merge_center= []
    
    for _, cnt_value in enumerate(contours):
        # smaller than MinArea; pass
        # area and calculate centerpoint each
        area = cv2.contourArea(cnt_value)
        if area > MinArea: 
            M = cv2.moments(cnt_value) # 넓이
            cX = int(M["m10"] / M["m00"]) # 무게중심의 x좌표
            cY = int(M["m01"] / M["m00"]) # 무게중심의 y좌표
            cnts_conditionpass.append([cX,cY,area])
            
    cnts_conditionpass.sort(key=lambda x: x[2]) # 작은것부터 합치기 시작해야 객체 분리 현상이 줄어듬
    
    count = 0
    # if none of contours pass codition : return []
    if len(cnts_conditionpass) == 0:
        return cnts_conditionpass
    
    # until all contours merge
    while count < len(cnts_conditionpass):
        not_around = False
        # make one big contour
        while not_around == False and len(cnts_conditionpass)>1 and count < len(cnts_conditionpass):
            zone1 = cnts_conditionpass[count] # count에 있는 contour에 대해서
            tmpZones = np.delete(cnts_conditionpass, count, 0) # 위의 contour 이후의 나머지 contour들을 복제
            for i in range(len(tmpZones)): # 복제된 ndarray에 있는 값 하나씩 비교
                zone2 = tmpZones[i]
                if(is_contour_around(zone1, zone2, threshold)):
                    tmpZones[i] = merge_contour(zone1, zone2)
                    cnts_conditionpass = tmpZones
                    not_around = False
                    break
                not_around = True
        # if it made; count +1
        count += 1
        
    # only return center point
    for i,coordinate in enumerate(cnts_conditionpass):
        center_X = coordinate[0]
        center_Y = coordinate[1]
        merge_center.append([int(center_X), int(center_Y)])
    
    return merge_center

# condition for combine; distance between two centerpoints
def is_contour_around(z1, z2, threshold):
    """contour들 끼리 가까움의 조건을 만족하는지 확인하는 함수
    Args :
        z1         (ndarray): 첫 번째 contour의 무게중심 좌표와 영역 넓이 (예 : [x1, y1, z1])
        z2         (ndarray): 두 번째 contour의 무게중심 좌표와 영역 넓이 (예 : [x2, y2, z2])
        threshold      (int): 가까움의 정도를 정해주는 하이퍼파라미터
    
    Returns :
        is_nearby     (bool): 두 점 사이의 거리가 threshold보다 작다면 True 아니라면 False
    """
    z1_center = (z1[0], z1[1])
    z2_center = (z2[0], z2[1])
    
    is_nearby = False
    
    if dist(z1_center, z2_center) < threshold:
        is_nearby = True
        return is_nearby
    else:
        is_nearby = False
        return is_nearby

# merge option; depend by area size
def merge_contour(z1, z2):
    """두 무게중심을 비율에 따라 합치는 함수
    Args :
        z1         (ndarray): 첫 번째 contour의 무게중심 좌표와 영역 넓이 (예 : [x1, y1, z1])
        z2         (ndarray): 두 번째 contour의 무게중심 좌표와 영역 넓이 (예 : [x2, y2, z2])
        
    Returns :
        merge_info (ndarray): 합쳐진 contour의 좌표와 영역 넓이 (예 : [x3, y3, z3])
    """
    sum_area = z1[2] + z2[2]
    
    center_X = int(z1[0]*(z1[2]/sum_area) + z2[0]*(z2[2]/sum_area))
    center_Y = int(z1[1]*(z1[2]/sum_area) + z2[1]*(z2[2]/sum_area))
    
    merge_info = [center_X, center_Y, sum_area/2]
    
    return merge_info