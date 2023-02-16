'''
setdata.yaml에 cctv_num의 이름으로 ROI값들이 저장됨
'''

import glob
import cv2
import yaml
import numpy as np

count = 358
name_org = 'Office_CCTV_B2_'
name_add = 'CCTV_B2_ADD_'

#path = '/mnt/c/Users/tom41/OneDrive/Desktop/output_b2/0' + str(count) + '.jpg'
path = '/mnt/c/Users/tom41/OneDrive/Desktop/cctv_b2/' + str(count) + '.jpg'

with open('setdata.yaml', 'r') as f:
    data1 = yaml.safe_load(f)

isdraw = False
result = ""
cctv_num = ""
x1, y1 = 0, 0
BLUE = (255, 0, 0)

data = {}
roi_data = ""

def yamlset():
    global data
    global count
    global cctv_num
    
    cctv_num = name_org + str(count)
    data[cctv_num] = {}
    data[cctv_num]["crop_size"] = []
    data[cctv_num]["pos"] = []
    data[cctv_num]["road"] = 0
    data[cctv_num]["roi"] = []
    print(cctv_num + ":\n crop_size: []\n pos:\n road: \n roi:")

    '''
    if count < 10:
        cctv_num = "WEBCAM0" + str(count)
        data[cctv_num] = {}
        data[cctv_num]["crop_size"] = []
        data[cctv_num]["pos"] = []
        data[cctv_num]["road"] = 0
        data[cctv_num]["roi"] = []
        print(cctv_num + ":\n crop_size: []\n pos:\n road: \n roi:")
    else:
        cctv_num = "CCCTV" + str(count)
        data[cctv_num] = {}
        data[cctv_num]["crop_size"] = []
        data[cctv_num]["pos"] = []
        data[cctv_num]["road"] = 0
        data[cctv_num]["roi"] = []
        print(cctv_num + ":\n crop_size: []\n pos:\n road: \n roi:")

    count+=1
'''

def clickcallback(event, x, y, flags, param):
    global isdraw
    global result
    global x1, y1
    global imgs
    global roi_data

    if event == cv2.EVENT_LBUTTONDOWN: # 좌표 기록 시작 및 ROI 박스 그리기 시작
        if isdraw:
            result = result + ", " + str(x) + ", " + str(y) + "]"
            roi_data = roi_data + f", {x}, {y}]"
            # roi_data.append(x)
            # roi_data.append(y)

            print(result)
            data[cctv_num]["roi"].append(roi_data)
            # roi_data.clear()
            isdraw = False
            w = x - x1
            h = y - y1
            if w > 0 and h > 0:
                cv2.rectangle(imgs, (x1, y1), (x, y), BLUE, 1)
        else:
            result = "  - [" + str(x) + ", " + str(y)
            roi_data = f"[{x}, {y}"
            # roi_data.append(x)
            # roi_data.append(y)
            isdraw = True
            x1 = x
            y1 = y
    
    elif event == cv2.EVENT_MOUSEMOVE:  # 마우스 이동
        if isdraw:
            img_draw = imgs.copy()
            cv2.rectangle(img_draw, (x1, y1), (x, y), BLUE, 1, cv2.LINE_AA)
            cv2.imshow('img', img_draw)
    
    # if event == cv2.EVENT_RBUTTONDOWN: # next draw
    #         print(x, y)

yamlset()

cv2.namedWindow('img')

for img in sorted(glob.glob(path)):
    imgs = cv2.imread(img)
    cv2.imshow("img", imgs)
    cv2.setMouseCallback("img", clickcallback)

    k = cv2.waitKey(0)

    if k == 27: # esc key
        data[cctv_num]["src"] = "rtsp://"
        # data[cctv_num]["uuid"] = "-uuid"
        print(" src: \n uuid:")
        print(data)
        yamlset()
        isdraw = False
        cv2.destroyAllWindows()
        

#  yaml 파일 출력
with open('setdata.yaml', 'w') as file:
    yaml.dump(data1, file, default_flow_style=False)
    yaml.dump(data, file, default_flow_style=False)