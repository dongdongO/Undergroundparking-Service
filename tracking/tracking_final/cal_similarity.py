from math import sqrt

# distance between two points
def cal_similarity(point1, point2):
    """두 점 사이의 거리 구하기
    Args :
        point1  (ndarray): 첫 번째 점의 좌표 (예 : [x1, y1])
        point2  (ndarray): 두 번째 점의 좌표 (예 : [x2, y2])
    
    Returns :
        distance  (float): 두 점 사이의 거리
    """
    x_length = point1[0] - point2[0]
    y_length = point1[1] - point2[1]
    
    distance = sqrt((x_length)**2 + (y_length)**2)
    
    return distance