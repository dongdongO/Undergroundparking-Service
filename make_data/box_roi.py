'''
setdata.yaml에 cctv_num의 이름으로 ROI값들이 저장됨
'''

import glob
import cv2
import yaml
import numpy as np

# name_org + count : name of the image & image path
count = 358
name_org = 'Office_CCTV_B2_'
path = '/mnt/c/Users/tom41/OneDrive/Desktop/cctv_b2/' + str(count) + '.jpg'

# add the result in setdata.yaml
with open('setdata.yaml', 'r') as f:
    data1 = yaml.safe_load(f)

# init
isdraw = False
result = ""
cctv_num = ""
x1, y1 = 0, 0
BLUE = (255, 0, 0)

data = {}
roi_data = ""

# add values in yaml
def yamlset():
    global data
    global count
    global cctv_num
    
    # key to be saved for each camera
    cctv_num = name_org + str(count)    # name
    data[cctv_num] = {}                 # init
    data[cctv_num]["crop_size"] = []    # crop_size
    data[cctv_num]["pos"] = []          # position
    data[cctv_num]["road"] = 0          # median y value of roads
    data[cctv_num]["roi"] = []          # ROI value for position
    print(cctv_num + ":\n crop_size: []\n pos:\n road: \n roi:")

# add ROI list in yaml
def clickcallback(event, x, y, flags, param):
    global isdraw
    global result
    global x1, y1
    global imgs
    global roi_data

    if event == cv2.EVENT_LBUTTONDOWN: # start record ROI values
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
    
    elif event == cv2.EVENT_MOUSEMOVE:
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

    # add key : src & uuid
    if k == 27: # exit : ESC
        data[cctv_num]["src"] = "rtsp://"
        print(" src: \n uuid:")
        print(data)
        yamlset()
        isdraw = False
        cv2.destroyAllWindows()
        
with open('setdata.yaml', 'w') as file:
    yaml.dump(data1, file, default_flow_style=False)
    yaml.dump(data, file, default_flow_style=False)