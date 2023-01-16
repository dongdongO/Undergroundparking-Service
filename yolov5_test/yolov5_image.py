import cv2
import torch

#image = cv2.imread("/mnt/c/Users/tom41/OneDrive/Desktop/안산그랑시티자이 CCTV/cctv_images_apt/cctv_org/b1/181.jpg", cv2.IMREAD_ANYCOLOR)
image = cv2.imread("/mnt/c/Users/tom41/OneDrive/Desktop/안산그랑시티자이 CCTV/cctv_images_apt/cctv_add/070.jpg", cv2.IMREAD_ANYCOLOR)

yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5m',
                            device='cuda:0' if torch.cuda.is_available() else 'cpu')  # 예측 모델
yolo_model.classes = [2]  # 예측 클래스 (사람)

results = yolo_model(image)
results_refine = results.pandas().xyxy[0].values
nms_car = len(results_refine)
if nms_car > 0:
    for bbox in results_refine:
        start_point = (int(bbox[0]), int(bbox[1]))
        end_point = (int(bbox[2]), int(bbox[3]))

        image = cv2.rectangle(image, start_point, end_point, (255, 0, 0), 3)


cv2.imshow("result", image)
cv2.waitKey()
cv2.destroyAllWindows()