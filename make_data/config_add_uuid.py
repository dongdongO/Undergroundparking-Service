import yaml
import requests
import json
from utils.general import LOGGER


def get_uuid(config, site):
    headers = {'Content-Type': 'application/json', 'X-API-KEY':'o0808kcg8sosssoc84gkkos0sss8kcok4s4k40so'}  # api key는 바꿔주어야 될 수도 있음
    # headers = {'Content-Type': 'application/json'}  # api key는 바꿔주어야 될 수도 있음
    url = f'https://{site}.watchmile.com/api/v1/parking/slot/'

    get_pos = get_yaml(config)

    # 서버에서 전체 주차면 상태 정보값 로딩
    slot_data = get_server(url, headers)
    total_state = slot_data.json()['lists']
    # with open('test.yaml', 'w', encoding='utf-8') as f:
    #     yaml.dump(total_state, f, default_style=False)

    result = {}  # 결과값 저장

    for key, value in get_pos.items():
        result[key] = value
        roi = []
        #print(key)
        for i in value['roi']:
            roi.append(str(i))
        
        result[key]['roi'] = roi
        uuid_list = []
        for idx in value['pos']:
            
            for slot in total_state:
                if slot['slot_name'] in idx:
                    uuid_list.append(slot['uuid'])
                    break

        #result['uuid'] = uuid_list
        result[key]['uuid'] = uuid_list
    return_yaml('result_add_ip.yaml', result)

def get_server(url: str, headers: str):
    """get을 사용한 서버 통신 함수

    Args:
        url (str): 주차장 서버 주소
        headers (str): 요청 헤더 값
    """
    try:
        r = requests.get(url, headers=headers)
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

def get_yaml(location: str):
    loads = dict()
    # yaml load from location
    with open(location) as f:
        loads = yaml.load(f, Loader=yaml.FullLoader)
    return loads

def return_yaml(location: str, return_dict):
    with open(location, 'w') as f:
        yaml.dump(return_dict, f)

get_uuid('add_ip.yaml', 'ansan-grancity-xi')