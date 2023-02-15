import argparse
import os
import sys
import time
from pathlib import Path
import datetime
import yaml
import cv2
from check_state import inout, double_inout
from transmit_server import sendstate2server
from utils.general import LOGGER
from utils.general import print_args
from dataloader import LoadData
from detector import Detector
from collections import deque, defaultdict
from QueueCheckService import QueueCheckService
from verify import verify
from mqtt.Login_MQTT import login_mqtt
from mqtt.Service_MQTT import mqtt_data_client, publish_pks_data, check_token_is_expired

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative


def run(mode, algorithm, config_file, service, send_mqtt,
        weights, source, data, imgsz, conf_thres, iou_thres, max_det, device, view_img, save_txt, save_conf, save_crop,
        nosave, classes, agnostic_nms, augment, visualize, update, project, name, exist_ok, line_thickness, hide_labels,
        hide_conf, half, dnn,
        ):
    """영상분석 실행 프로세스
    Args:
        mode        (int): 멀티프로세싱 사용 시 영상분석할 카메라 그룹 설정 (1, 2, ...)
        algorithm   (str): 주차 점유 판단 알고리즘 선택 (occupancy: ROI를 이용한 점유 판단, trace: 궤적을 이용한 점유 판단)
        config_file (str): 카메라 설정 정보 (rtsp_url, uuid, slot_id, roi, road)가 저장된 파일 경로 (.yaml)
        service    (bool): 주차 점유 판단 결과 API 서버 전송 여부 (True: 전송, False: 전송 안함)
        send_mqtt  (bool): 주차 점유 판단 결과 MQTT 서버 전송 여부 (True: 전송, False: 전송 안함)
        weights, ...,    : argument parser에 의해 얻은 실행 변수 및 설정값
    Examples:
        >>> run(1, 'occupancy', **vars(opt))
    Raises:
        RecursionError, AssertionError: 카메라 접속이 불가하거나 원활하지 않은 경우 발생
    """
    cams = dict()
    with open(config_file) as f:
        all_cams = yaml.load(f, Loader=yaml.FullLoader)

    for cam in all_cams.items():
        cams[cam[0]] = cam[1]

    detector = Detector(opt)
    dataset = LoadData(mode, cams)
    bs = len(dataset)  # batch_size
    state = defaultdict(deque)
    for key in dataset.__cams__:
        state[key]
    state = dict(state)

    if send_mqtt:
        # Image Log Queue Check Service
        queueCheckService = QueueCheckService()
        # MQTT Client
        logins = login_mqtt()
        topic_class = 'log'
        service_mqtt_client = mqtt_data_client(logins, topic_class)
        parkingLot = 'ansan-grancity-xi'
        parkingFloor = 'b1_b2'
        service_topic = 'wlogs/device/service/' + logins.clientID + '/' + topic_class + '/video/' + parkingLot + '/' + parkingFloor
        start = time.time()

    # Run inference
    detector.model_warmup(bs)  # warmup
    for cam_seq, cam, frame, vid_cap, webcam, s in dataset:
        try:
            bbox_by_cropped = list()
            if 'crop_size' in cam:
                # 이미지 crop 후 재인식
                crop_size = cam['crop_size']
                if len(crop_size) == 4:
                    cropped = frame[crop_size[1]: crop_size[3], crop_size[0]: crop_size[2]]
                    c_data, c_annotator, c_view_img = detector.detect(cropped, webcam)
                    for c_box in c_data:
                        add_left, add_top, label, box = crop_size[0], crop_size[1], c_box['label'], c_box['box']
                        bbox_by_cropped.append({'label': label, 'box': [int(box[0] + add_left), int(box[1] + add_top),
                                                                        int(box[2] + add_left), int(box[3] + add_top)]})
            data, annotator, view_img = detector.detect(frame, webcam)

            boxes = list()
            for box in data:
                boxes.append(box['box'])
                annotator.box_label(box['box'], box['label'], color=(0, 0, 255))

            boxes_crop = list()
            for box_crop in bbox_by_cropped:
                boxes_crop.append(box_crop['box'])
            for box_crop in bbox_by_cropped:
                annotator.box_label(box_crop['box'], box_crop['label'], color=(255, 0, 255))
                cv2.rectangle(annotator.result(), (crop_size[0], crop_size[1]), (crop_size[2], crop_size[3]),
                              (255, 0, 0), 1)
                boxes.append(box_crop['box'])

            cam['state'] = inout(annotator.result(), cam, boxes, cam['road'])
            LOGGER.info(f'{cam_seq} - Parking state with occupancy: {cam["state"]}')

            if 'double_rois' in cam.keys():
                cam['state'] = double_inout(annotator.result(), cam, boxes, cam['road'])
                LOGGER.info(f'{cam_seq} - Parking state with double parking: {cam["state"]}')

            if send_mqtt:
                # 원본 이미지 저장
                curr_time = datetime.datetime.strftime(datetime.datetime.now(), "%y%m%d_%H%M%S")
                imgpath = f'./images/{cam_seq}'
                if ('prev_state' in cam) and (cam['prev_state'] != cam['state']):
                    # 이전 주차 상태와 현재의 주차 상태가 상이할 때 이미지 저장
                    if not os.path.exists(imgpath):
                        os.makedirs(imgpath)
                    imgpath = imgpath + f'/{cam_seq}_{curr_time}.jpg'
                    cv2.imwrite(imgpath, frame)
                elif 'prev_state' not in cam.keys():
                    # 최초 실행시에도 이미지 저장
                    if not os.path.exists(imgpath):
                        os.makedirs(imgpath)
                    imgpath = imgpath + f'/{cam_seq}_{curr_time}.jpg'
                    cv2.imwrite(imgpath, frame)
                else:
                    imgpath = None

                result = insert_data(cam_seq, cam, boxes, imgpath)

                # 여기까지 기존의 로그 완성
                # 기존의 로그를 건들지 않고 새 로그 생성
                queueCheckService.setterCam(cam)
                queueCheckService.setterResult(result)
                queueCheckService.checkCCTVId(cam_seq)  # insert cctvID(cam_seq)

            cam["state"] = verify(cam, cam_seq, state, num=1)
            if service and cam["state"] is not None:
                sendstate2server(cam, site='ansan-grancity-xi')  # Send parking state to API server
                cam['prev_state'] = cam['state']

            if send_mqtt and cam["state"] is not None:
                queueCheckService.insertModelList(list(cam['state'].values()))
                queueCheckService.checkImg(cam_seq, list(cam['state'].values()), frame)

                # MQTT publish
                if (time.time() - start) / 60 > 30:
                    cp = check_token_is_expired(service_mqtt_client)
                    service_mqtt_client.password = cp
                    service_mqtt_client.stop()
                    service_mqtt_client.setUser(pwd=cp)
                    service_mqtt_client.start()
                    start = time.time()
                publish_pks_data(service_mqtt_client, service_topic, queueCheckService.getterResult(), parkingFloor)

            # Save results
            if not os.path.exists(str(detector.save_dir) + '/images'):
                os.mkdir(str(detector.save_dir) + '/images')
            cv2.imwrite(str(detector.save_dir / 'images' / cam_seq) + '.jpg', annotator.result())

            # Display results
            # if view_img:
                # cv2.namedWindow(cam_seq, cv2.WINDOW_AUTOSIZE)
                # cv2.moveWindow(cam_seq, 0, 0)
                # cv2.imshow(cam_seq, annotator.result())
                # cv2.waitKey(33)

        except:
            # 영상분석이 실패한 경우 (예. 영상 접속 불가 등) 다음 영상으로 skip
            LOGGER.exception("Detection Failed!")
            continue


def insert_data(cam_seq, cam, boxes, imgpath):
    """Data 서버에 삽입할 정보 생성
    Args:
        cam_seq     (str): 카메라 ID
        cam        (dict): 한 카메라 설정 정보 (rtsp url, road, uuid, slot_id, borderline/roi)
        boxes      (list): 한 카메라 내 인식된 차량의 bounding box 좌표 리스트
        imgpath     (str): 결과 이미지 저장 경로
    Returns:
        dict: Data 서버에 삽입할 정보 딕셔너리
    """
    result = dict()
    result['cctv-id'] = cam_seq
    result['model-name'] = 'yolov5'
    result['model-version'] = 6.0
    result['pks-id-list'] = cam['pos']
    result['roi-box-coord-list'] = cam['roi']
    result['predicted-by-model-list'] = list(cam['state'].values())
    result['bounding-box-coord-list'] = boxes
    result['img-path'] = os.path.abspath(imgpath) if imgpath is not None else None
    result['region'] = 'Anyang'
    result['pk-name'] = 'Anyang2_SKV1'

    return result


def parse_opt():
    """프로세스 실행 매개변수 목록
        Returns:
            namespace: 프로세스 실행 매개변수 및 설정값
        Examples:
            >>> python run_final.py --weights yolov5l.pt --device 0

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=ROOT / 'yolov5s.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default=ROOT / 'data/images', help='file/dir/URL/glob, 0 for webcam')
    parser.add_argument('--data', type=str, default=ROOT / 'data/coco128.yaml', help='(optional) dataset.yaml path')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='show results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default=ROOT / 'runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    parser.add_argument('--send-mqtt', action='store_true', help='send results to mqtt server')
    parser.add_argument('--service', action='store_true', help='send results to API server')
    parser.add_argument('--config-file', type=str, default='config_AnsanXi_APT2.yaml', help='yaml config file path')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    print_args(FILE.stem, opt)
    return opt


def main(opt):
    run(1, 'occupancy', **vars(opt))
    # with ProcessPoolExecutor() as executor:
    #     procs = [executor.submit(run, 1, 'trace', **vars(opt)), executor.submit(run, 1, 'occupancy', **vars(opt))]


if __name__ == "__main__":
    opt = parse_opt()
    main(opt)
