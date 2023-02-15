import requests
import json
from utils.general import LOGGER


def sendstate2server(cam, site):
    """주차 점유 상태 전송
    주차면의 점유 상태를 앱 서비스용 API 서버에 전송
    Args:
        cam     (dict): 한 카메라에 대한 정보 (기준 도로 좌표, 영상 접속 주소, 주차면별 uuid, slot_id, ROI 좌표)
        site     (str): 주차장 이름 (skv1-ay2: 안양2차 SKV1, hobanpark: 호반파크 2관, cheonho: 천호/강동역 공영주차장, 기타 등)

    """
    headers = {'Content-Type': 'application/json', 'X-API-KEY': 'o0808kcg8sosssoc84gkkos0sss8kcok4s4k40so'}
    url = f'{"https" if site != "cheonho" else "http"}://{site}.watchmile.com/api/v1/parking/slot/'
    try:
        for idx, state in enumerate(cam['state'].values()):
            uuid = cam['uuid'][idx]
            if 'prev_state' in cam:
                # 최초 프로세스 실행 시를 제외하고 이전 영상 프레임에서의 분석 결과 호출
                prev_state = cam['prev_state'][cam['pos'][idx]]
            else:
                # 최초 프로세스 실행 시 이전의 주차 상태를 API 서버에서 호출
                # LOGGER.info(url+uuid)
                # slot_data = get(url + uuid)
                # prev_state = slot_data.json()['result']['slot_status']
                prev_state = 'none'
                if state != prev_state:
                    put(url + 'state/' + uuid, {'slot_status': state}, headers)
                    LOGGER.info(f'Parking state updated in {cam["pos"][idx]}')
                continue
            if state != prev_state:
                # 현재 주차 점유 상태와 이전의 상태가 상이할 때만 API 서버로 결과 전송
                put(url + 'state/' + uuid, {'slot_status': state}, headers)
                LOGGER.info(f'Parking state updated in {cam["pos"][idx]}')
            else:
                continue

    except Exception as e:
        LOGGER.exception(e)
        pass


# 관제 서버에 주차 상태를 전송
def put(url1, data, headers):
    try:
        r = requests.put(url1, data=json.dumps(data), headers=headers)
        if r.status_code != 200:  # 전송 성공시 상태 코드 출력
            LOGGER.info("HTTP Error code: ", r.status_code)
        else:
            LOGGER.info("transmission success!")
    # 오류 발생시 예외처리
    except requests.exceptions.Timeout as errd:
        LOGGER.exception("Timeout Error : ", errd)
    except requests.exceptions.ConnectionError as errc:
        LOGGER.exception("Error Connecting : ", errc)
    except requests.exceptions.HTTPError as errb:
        LOGGER.exception("Http Error : ", errb)
        # Any Error except upper exception
    except requests.exceptions.RequestException as erra:
        LOGGER.exception("AnyException : ", erra)


# 주차면 API 서버에서 기존 주차면 상태 수신
def get(url1):
    try:
        r = requests.get(url1)
        if r.status_code != 200:  # 전송 실패시 상태 코드 출력
            LOGGER.info("HTTP Error code: ", r.status_code)
        return r
    # 오류 발생시 예외처리
    except requests.exceptions.Timeout as errd:
        LOGGER.exception("Timeout Error : ", errd)
    except requests.exceptions.ConnectionError as errc:
        LOGGER.exception("Error Connecting : ", errc)
    except requests.exceptions.HTTPError as errb:
        LOGGER.exception("Http Error : ", errb)
        # Any Error except upper exception
    except requests.exceptions.RequestException as erra:
        LOGGER.exception("AnyException : ", erra)
