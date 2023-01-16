import cv2
import time
import numpy as np
from numpy.lib.function_base import diff

i = 0 # 이런 방식 말고 더 좋은 방식이 있을꺼 같은데 일단 pass
capture = cv2.VideoCapture('./CCTV17_crop_1.mp4')

width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 프레임 정보를 저장해놓을 변수를 선언한다. 
# RGB : np.zeros((height,width,3)) || GRAY : np.zeros((height,width))
first_frame = np.zeros((height,width,3))
second_frame = np.zeros((height, width,3))

# 영상에서 첫 프레임과 두번째 프레임을 저장한다 
while cv2.waitKey(33) < 0:
    start = time.time()
    i += 1
    
    return_value, frame = capture.read()
    # 비디오 프레임 정보가 있으면 계속 진행 
    if return_value:
        pass
    else : 
        print('비디오가 끝났거나 오류가 있습니다')
        break
    # frame차를 구하기 위해 전 frame을 저장 : 아쉬운건 이 방법이 최선? 복잡도가 너무 올라감
    if i%2 == 0:
        first_frame = frame
    else:
        second_frame = frame

    sub_image_RGB = second_frame - first_frame

    cv2.imshow('substract_RGB', sub_image_RGB)
    cv2.imshow('original', frame)

capture.release()
cv2.destroyAllWindows()