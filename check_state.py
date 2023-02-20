import cv2

# BGR 색상값 기준
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
PURPLE = (255, 0, 255)


def inout(img, cam, bboxes, road):
    """인식된 차량의 bounding box와 설정한 ROI box로 주차 점유여부 판단
    Args:
        img      (ndarray): 원본 이미지
        cam         (dict): 한 카메라 설정 정보 (double_rois, double_slots, pos, road, roi, src, uuid)
        bboxes      (list): Yolov5가 인식한 차량의 bounding box 좌표 리스트 (xyxy)
        road         (int): 도로의 x 좌표 (수직선) -> 차량의 우측좌측 기준 담당

    Returns:
        inouts: 한 카메라에 대한 각 주차면의 점유 상태 딕셔너리 (예: {'1-x2-y3-1': 'free', '1-x2-y3-2': 'in'})
    """
    inouts = dict()  # 각 주차면별 점유 상태 딕셔너리

    for idx, slot_id in enumerate(cam['pos']):
        roi = cam['roi'][idx]   # 해당 pos에 대한 roi list값
        cv2.rectangle(img, (roi[0], roi[1]), (roi[2], roi[3]), GREEN, 1)  # roi 초록박스로 그리기
        if not bboxes:
            # 카메라 내 인식된 차량이 한 대도 없을 때
            inouts[slot_id] = 'free'
        else:
            # 카메라 내 인식된 차량이 한 대 이상일 때
            for bbox in bboxes:
                is_left = (bbox[0] + bbox[2]) / 2 < road  # 차량의 bounding box 중점이 도로 기준으로 좌측에 있는지 확인
                is_y_inside = roi[1] < bbox[3] < roi[3]  # 차량의 bounding box의 y좌표가 ROI 내부에 포함되는지 확인
                is_x_right_inside, is_x_left_inside = roi[0] < bbox[2] < roi[2], roi[0] < bbox[0] < roi[2] # 차량이 좌,우측에 있을 조건
                if is_left and is_y_inside and is_x_right_inside:   # 차량이 왼쪽에 있고 우측 하단점의 x,y 좌표가 roi안에 있다면
                    # 차량이 도로 좌측에 주차된 경우 bounding box의 우측 하단점 기준으로 점유 판단
                    cv2.rectangle(img, (roi[0], roi[1]), (roi[2], roi[3]), YELLOW, 1)  # 점유된 주차면의 ROI는 노란색 박스
                    inouts[slot_id] = 'in'
                    break
                elif not is_left and is_y_inside and is_x_left_inside:  # 차량이 우측에 있고 좌측 하단점의 x,y 좌표가 roi안에 있다면
                    # 차량이 도로 우측에 주차된 경우 bounding box의 좌측 하단점 기준으로 점유 판단
                    cv2.rectangle(img, (roi[0], roi[1]), (roi[2], roi[3]), YELLOW, 1)  # 점유된 주차면의 ROI는 노란색 박스
                    inouts[slot_id] = 'in'
                    break
                else:
                    # 점유된 차가 없다면 원상태의 초록색 박스
                    cv2.rectangle(img, (roi[0], roi[1]), (roi[2], roi[3]), GREEN, 1)
                    inouts[slot_id] = 'free'
    
    # 결과값이 run_final.py 에서 cam['state']에 저장
    return inouts


def double_inout(img, cam, bboxes, road):
    """인식된 차량의 bounding box와 설정한 ROI box로 이중주차 여부 판단
    Args:
        img      (ndarray): 원본 이미지
        cam         (dict): 한 카메라 설정 정보 (double_rois, double_slots, pos, road, roi, src, uuid)
        bboxes      (list): Yolov5가 인식한 차량의 bounding box 좌표 리스트 (xyxy)
        road         (int): 도로의 x 좌표 (수직선) -> 차량의 우측좌측 기준 담당

    Returns:
        dict: 한 카메라에 대한 각 주차면의 점유 상태 딕셔너리 (예: {'1-x2-y3-1': 'free', '1-x2-y3-2': 'in'})
    
    => inout과 같지만 '이중주차로 영향을 받는 기존의 주차면은 모두 점유된 것으로 강제 처리' 추가
    """
    for idx, double_roi in enumerate(cam['double_rois']):
        if not bboxes:
            # 카메라 내 인식된 차량이 한 대도 없을 때
            break
        else:
            # 카메라 내 인식된 차량이 한 대 이상일 때
            for bbox in bboxes:
                is_left = (bbox[0] + bbox[2]) / 2 < road  # 차량의 bounding box가 도로 기준으로 좌측에 있는지 확인
                is_y_inside = double_roi[1] < bbox[3] < double_roi[3]  # 차량의 bounding box의 y좌표가 이중주차의 ROI 내부에 포함되는지 확인
                is_x_right_inside, is_x_left_inside = double_roi[0] < bbox[2] < double_roi[2], double_roi[0] < bbox[0] < double_roi[2]
                if is_left and is_y_inside and is_x_right_inside:
                    # 차량이 도로 좌측에 주차된 경우 bounding box의 우측 하단점 기준으로 점유 판단
                    cv2.rectangle(img, (double_roi[0], double_roi[1]), (double_roi[2], double_roi[3]), PURPLE, 1)  # 이중주차 발생시 해당 구역의 ROI는 보라색으로 표시
                    for double_slot in cam['double_slots'][idx]:  # 이중주차로 영향을 받는 기존의 주차면은 모두 점유된 것으로 강제 처리
                        cam['state'][double_slot] = 'in'
                    break
                elif not is_left and is_y_inside and is_x_left_inside:
                    # 차량이 도로 우측에 주차된 경우 bounding box의 좌측 하단점 기준으로 점유 판단
                    cv2.rectangle(img, (double_roi[0], double_roi[1]), (double_roi[2], double_roi[3]), PURPLE, 1)  # 이중주차 발생시 해당 구역의 ROI는 보라색으로 표시
                    for double_slot in cam['double_slots'][idx]:  # 이중주차로 영향을 받는 기존의 주차면은 모두 점유된 것으로 강제 처리
                        cam['state'][double_slot] = 'in'
                    break
                else:
                    continue
    return cam['state']


def occupancy_inout(img, b_lines, cam):
    """인식된 차량의 bounding line과 설정한 LOI로 주차 점유여부 판단
    Args:
        img    (ndarray): 원본 이미지
        b_lines   (list): 한 카메라에 대해 인식된 차량의 좌상단에서 우하단 지점까지의 직선 리스트
        cam       (dict): 한 카메라 설정 정보 (rtsp url, road, uuid, slot_id, borderline)

    Returns:
        dict: 한 카메라에 대한 각 주차면별 주차 점유 상태 딕셔너리 (예: {'1-x2-y4-1': 'in', '1-x2-y4-2': 'free'})
    """
    inouts = dict()  # 각 주차면별 주차 점유 상태 딕셔너리

    for idx, slot_id in enumerate(cam['pos']):
        loi = cam['loi'][idx]
        cv2.line(img, (loi[0], loi[1]), (loi[2], loi[3]), GREEN, 2, cv2.LINE_AA)
        if len(b_lines) != 0:
            # 인식된 차량이 존재하는지 확인
            for bound_line in b_lines:
                # 차량의 좌측 상단에서 우측 하단 지점까지의 직선 그리기
                x1, y1, x2, y2 = loi[0], loi[1], loi[2], loi[3]
                x3, y3, x4, y4 = bound_line[0], bound_line[1], bound_line[2], bound_line[3]

                if (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4) != 0:
                    # 주차선과 차량 직선이 교차하는지 확인 후 교차하면 교점의 x, y 좌표 계산
                    x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (x3 - x4) * (y1 - y2))
                    y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (x3 - x4) * (y1 - y2))
                    if (x1 <= x <= x2 or x2 <= x <= x1) and (y1 <= y <= y2 or y2 <= y <= y1) and \
                        (x3 <= x <= x4 or x4 <= x <= x3) and (y3 <= y <= y4 or y4 <= y <= y3):
                        # 교점이 주차선 상에 위치한지 확인
                        cv2.line(img, (loi[0], loi[1]), (loi[2], loi[3]), RED, 2, lineType=cv2.LINE_AA)
                        inouts[slot_id] = 'in'
                        # 교점이 존재하면 주차면 점유 처리, 그렇지 않으면 공면으로 처리
                        break
                    else:
                        inouts[slot_id] = 'free'
                else:
                    inouts[slot_id] = 'free'
        else:
            inouts[slot_id] = 'free'

    return inouts


# 이거 안씀 폐기
def find_intersection(img, trajectories, cam, cam_seq):
    """객체 추적 알고리즘을 이용한 주차선 통과 여부 판단
    Args:
        img          (ndarray): 원본 이미지
        trajectories    (dict): 모든 카메라에 대해 이전 이미지와 현재 이미지의 차량 bounding box의 중심 하단 좌표
        cam             (dict): 한 카메라 설정 정보 (rtsp url, road, uuid, slot_id, borderline)
        cam_seq          (str): 카메라 ID

    Returns:
        dict: 한 카메라에 대한 각 주차면별 주차 점유 상태 딕셔너리 (예. {'1-x2-y4-1': 'in', '1-x2-y4-2': 'free'})
        dict: 한 카메라에 대한 각 주차면별 차량 주차선 통과 여부 딕셔너리 (True: 통과) (예. {'1-x2-y4-1': False, '1-x2-y4-2': True})
    """
    inouts = dict()  # 각 주차면별 주차 점유 상태 딕셔너리
    isintersects = dict()  # 각 카메라별 주차선과 차량 궤적 교차 여부 딕셔너리
    for idx, slot_id in enumerate(cam['pos']):
        borderline = cam['borderline'][idx]
        cv2.line(img, (borderline[0], borderline[1]), (borderline[2], borderline[3]), GREEN, 2, cv2.LINE_AA)
        if len(trajectories[cam_seq]) != 0:
            # 차량 궤적이 존재하는지 확인
            for trajectory in trajectories[cam_seq]:
                # 이전 이미지와 현재 이미지의 차량 bbox의 중심 (하단) 좌표를 연결하는 유향직선 그리기
                x1, y1, x2, y2 = borderline[0], borderline[1], borderline[2], borderline[3]
                x3, y3, x4, y4 = trajectory[0][0], trajectory[0][1], trajectory[1][0], trajectory[1][1]
                cv2.arrowedLine(img, (x3, y3), (x4, y4), BLUE, 2, line_type=cv2.LINE_AA)

                if (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4) != 0:
                    # 주차선과 궤적이 교차하는지 확인 후 교차하면 교점의 x, y 좌표 계산
                    x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (x3 - x4) * (y1 - y2))
                    y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (x3 - x4) * (y1 - y2))
                    if (x3 <= x <= x4 or x4 <= x <= x3) and (y3 <= y <= y4 or y4 <= y <= y3) and x1 <= x <= x2 and (y1 <= y <= y2 or y2 <= y <= y1):
                        # 교점이 궤적 선상에 위치한지 확인
                        isintersects[slot_id] = True
                        cv2.line(img, (borderline[0], borderline[1]), (borderline[2], borderline[3]), RED, 2, cv2.LINE_AA)
                        # 교점이 존재하면 차량 이동방향으로 점유 여부 판단, 그렇지 않으면 None으로 처리 (판단불가)
                        inouts[slot_id] = trace_inout(borderline, [x3, y3, x4, y4], inouts, slot_id, cam['road'])
                        break
                    else:
                        isintersects[slot_id] = False
                        inouts[slot_id] = None
                else:
                    isintersects[slot_id] = False
                    inouts[slot_id] = None
        else:
            inouts[slot_id] = None

    return inouts, isintersects


# 이거 안씀 폐기
def trace_inout(borderline, trace, inouts, slot_id, road):
    """객체 추적 알고리즘을 이용한 주차 점유 판단
    Args:
        borderline  (list): 한 주차선의 양 끝점 (x1, y1, x2, y2)
        trace       (list): 주차선과 교차하는 차량 궤적의 양 끝점 (x1, y1, x2, y2)
        inouts      (dict): 한 카메라에 대한 각 주차면별 주차 점유 상태 딕셔너리 (예. {'1-x2-y4-1': 'in', '1-x2-y4-2': 'free'})
        slot_id      (str): 주차면 ID (예. '1-y2-x3-2')
        road         (int): 도로의 x 좌표 (수직선)

    Returns:
        dict: 한 카메라에 대한 각 주차면별 주차 점유 상태 딕셔너리 (예. {'1-x2-y4-1': 'in', '1-x2-y4-2': 'free'})
    """
    if (borderline[0] + borderline[2]) / 2 < road:
        # 주차면이 기준선 좌측에 위치한 경우
        if trace[0] - trace[2] > 0 or trace[1] - trace[3] > 0:
            # 차량이 왼쪽 또는 위쪽으로 이동한 경우
            inouts[slot_id] = 'in'
        else:
            inouts[slot_id] = 'free'
    else:
        # 주차면이 기준선 우측에 위치한 경우
        if trace[0] - trace[2] < 0 or trace[1] - trace[3] > 0:
            inouts[slot_id] = 'in'
        else:
            inouts[slot_id] = 'free'

    return inouts[slot_id]
