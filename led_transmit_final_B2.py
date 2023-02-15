import requests
from utils.general import LOGGER
# from general import LOGGER
import yaml
import socket
import threading
import time

def total_count(site: str, zone: str):
    """전체 주차면 관리 함수

    전체 주차면 정보를 받아온 뒤 전처리함

    Args:
        site (str): 주차장 이름
        zone (str): 주차장 구역 이름
    """
    headers = {'Content-Type': 'application/json', 'X-API-KEY':'o0808kcg8sosssoc84gkkos0sss8kcok4s4k40so'}  # api key는 바꿔주어야 될 수도 있음
    url = f'https://{site}.watchmile.com/api/v1/parking/slot/led/'

    # 지하 1층, 지하 2층 주차면 상태값 저장 dict
    state_list_b1 = {}
    state_list_b2 = {}

    for i in range(1, 26):  # 지하 1층 주차면 상태값 초기화
        if i == 20 or i == 21 or i == 23 or i == 24:
            continue
        else:
            state_list_b1[i] = {'normal': 0, 'electric': 0, 'handicap': 0, 'compact': 0, 'double': 0}
    
    for i in range(1, 17):  # 지하 2층 주차면 상태값 초기화
        state_list_b2[i] = {'normal': 0, 'electric': 0, 'handicap': 0, 'compact': 0, 'double': 0}

    # tcp('B1', state_list_b1, url, headers=headers, zone=zone)
    if zone != 'store':  # 수변상가는 B2층이 없음
        tcp('B2', state_list_b2, url, headers=headers, zone=zone)

# def type_check(state: dict, num_type: str):  # 자체 카운팅해야할 경우 사용
#     if num_type == 'normal' or num_type == 'wash':
#         state['normal'] += 1
#     elif num_type == 'electric':
#         state['elctric'] += 1
#     elif num_type == 'handicap':
#         state['handicap'] += 1
#     elif num_type == 'compact':
#         state['compact'] += 1
#     elif num_type == 'doubleParking':
#         state['double'] += 1
#     return state

def convert_number_to_special_char(number):
    """숫자를 특수 문자로 변환하는 함수

    Args:
        number (int): 변환할 숫자
    """
    # base = 0x22
    # code_point = base + number
    # special_char = '/U' + hex(code_point)[2:].upper()
    if number < 10:
        special_char = f'/U0{22 + number}'
    elif number < 100:
        first_char = f'/U0{22 + int(number / 10)}'
        special_char = first_char + f'/U0{22 + (number % 10)}'
    else:
        first_char = f'/U0{22 + int(number / 100)}'
        second_char = first_char + f'/U0{22 + int((number % 100) / 10)}'
        special_char = second_char + f'/U0{22 + (number % 10)}'

    return special_char
    
def get_state(url: str, headers: str):
    """get을 사용하여 서버에서 전체 주차면 상태정보를 가져오는 함수

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

def get_sum(url: str, headers: str):
    """get을 사용하여 서버에서 주차면 구역별 종류별 합계를 가져오는 함수

    Args:
        url (str): 주차장 서버 주소
        headers (str): 요청 헤더 값
    """
    try:
        r = requests.get(url + 'led', headers=headers)
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
    pads = dict()
    # yaml load from location
    with open(location) as f:
        pads = yaml.load(f, Loader=yaml.FullLoader)
    return pads

def protocol_message(state_list: dict, size: int, zone: str, version: int):
    """전광판 메세지를 만드는 함수

    주차면의 점유 상태를 서비스용 전광판에 전송

    Args:
        state (dict): 현재 전광판 집계 정보
        size (int): 전광판 사이즈
        zone (str): 송신을 진행할 구역
        version (int): ver1 단면 전광판, ver2 양면 전광판
    """
    message = ''
    msg = ['', '', '']  # 60cm 전광판의 경우 메시지 리스트에 3가지 값을 가짐

    if size == 60:
        num = state_list['handicap']
        str_num = convert_number_to_special_char(num)
        if version == 1:
            if len(str_num) > 10: msg[0] = f'![000/U010/C6장애인면/U011   {str_num}   /U010/C6장애인면/U011   {str_num}   !]'
            elif len(str_num) > 5: msg[0] = f'![000/U010/C6장애인면/U011    {str_num}    /U010/C6장애인면/U011    {str_num}    !]'
            else: msg[0] = f'![000/U010/C6장애인면/U011     {str_num}     /U010/C6장애인면/U011     {str_num}     !]'
        elif version == 2:
            if len(str_num) > 10: msg[0] = f'![000/U010/C6장애인면/U011/U010/C6장애인면/U011   {str_num}      {str_num}   !]'  # ver 2
            elif len(str_num) > 5: msg[0] = f'![000/U010/C6장애인면/U011/U010/C6장애인면/U011    {str_num}        {str_num}    !]'  # ver 2
            else: msg[0] = f'![000/U010/C6장애인면/U011/U010/C6장애인면/U011     {str_num}          {str_num}     !]'  # ver 2

        num = state_list['normal']
        str_num = convert_number_to_special_char(num)
        if version == 1:
            if len(str_num) > 10: msg[1] = f'![000/U010 /C7일반면 /U011   {str_num}   /U010 /C7일반면 /U011   {str_num}   !]'
            elif len(str_num) > 5: msg[1] = f'![000/U010 /C7일반면 /U011    {str_num}    /U010 /C7일반면 /U011    {str_num}    !]'
            else: msg[1] = f'![000/U010 /C7일반면 /U011     {str_num}     /U010/ C7일반면 /U011     {str_num}     !]'
        elif version == 2:
            if len(str_num) > 10: msg[1] = f'![000/U010 /C7일반면 /U011/U010 /C7일반면 /U011   {str_num}      {str_num}   !]'  # ver 2
            elif len(str_num) > 5: msg[1] = f'![000/U010 /C7일반면 /U011/U010 /C7일반면 /U011    {str_num}        {str_num}    !]'  # ver 2
            else: msg[1] = f'![000/U010 /C7일반면 /U011/U010 /C7일반면 /U011     {str_num}          {str_num}     !]'  # ver 2

        num = state_list['double']
        str_num = convert_number_to_special_char(num)
        if version == 1:
            if len(str_num) > 10: msg[2] = f'![000/U010/C1이중주차/U011   {str_num}   /U010/C1이중주차/U011   {str_num}   !]'
            elif len(str_num) > 5: msg[2] = f'![000/U010/C1이중주차/U011    {str_num}    /U010/C1이중주차/U011    {str_num}    !]'
            else: msg[2] = f'![000/U010/C1이중주차/U011     {str_num}     /U010/C1이중주차/U011     {str_num}     !]'
        elif version == 2:
            if len(str_num) > 10: msg[2] = f'![000/U010/C1이중주차/U011/U010/C1이중주차/U011   {str_num}      {str_num}   !]'  # ver 2
            elif len(str_num) > 5: msg[2] = f'![000/U010/C1이중주차/U011/U010/C1이중주차/U011    {str_num}        {str_num}    !]'  # ver 2
            else: msg[2] = f'![000/U010/C1이중주차/U011/U010/C1이중주차/U011     {str_num}          {str_num}     !]'  # ver 2
        return msg

    elif size == 100:
        num_normal = number_to_char(state_list['normal'])
        num_handicap = number_to_char(state_list['handicap'])
        num_compact = number_to_char(state_list['compact'])
        
        if zone == 'store':
            num_operation = number_to_char(state_list['operation'])
            message = f'![000/U012/C7일반/C5작업/C6장애/C3경차/U012  {num_normal}{num_operation}{num_handicap}{num_compact}  !]'
        else:
            num_electric = number_to_char(state_list['electric'])
            num_double = number_to_char(state_list['double'])
            message = f'![000/C7일반/C2전기/C6장애/C3경차/C1이중{num_normal}{num_electric}{num_handicap}{num_compact}{num_double}!]'

    elif size == 160:
        num_normal = number_to_char(state_list['normal'])
        num_handicap = number_to_char(state_list['handicap'])
        num_compact = number_to_char(state_list['compact'])

        if zone == 'store':
            num_operation = number_to_char(state_list['operation'])
            message = f'![000/U012/C7일반  /C6장애  /C3경차  /C5작업  /C2전기/U012  {num_normal}  {num_handicap}  {num_compact}  {num_operation}  !]'
        else:
            num_electric = number_to_char(state_list['electric'])
            num_double = number_to_char(state_list['double'])
            message = f'![000/U012/C7일반  /C6장애  /C3경차  /C1이중  /C2전기/U012  {num_normal}  {num_handicap}  {num_compact}  {num_double}  {num_electric}  !]'

    return message

def number_to_char(number: int) -> str:
    if number >= 1000: 
        char = str(number)
    elif number >= 100: 
        char = f' {str(number)}'
    elif number >= 10: 
        char = f' {str(number)} '
    elif number == 0:
        char = ' 00 '
    else: 
        char = f'  {str(number)} '

    return char

def tcp(floor, state, url, headers, zone):
    """전광판 통신 함수

    주차면의 점유 상태를 서비스용 전광판에 전송

    Args:
        floor  (str): 현재 층 번호
        state (dict): 전체 주차면 집계 정보
        url (str): URL
        headers (str): HTTP headers
        zone (str): 전광판 송신 구역
    """

    test_case = False # 전광판 송신 전 메시지 형식 테스트용 변수, True일 경우 테스트
    version = 2 # 1 or 2, 2번의 경우 양면 전광판 형식

    default_ip = "192.168.202." if floor == 'B1' else "192.168.203."  # 지하 1층이면 202.xx, 지하 2층이면 203.xx
    # PORT = 5000               # 포트는 5000 고정
    
    slot_data =  get_sum(url, headers)
    zone_state = slot_data.json()['zone_sum']
    total_state = slot_data.json()['led']

    for i in state.keys():  # 60cm 전광판의 경우 스레드를 사용하여 동시에 뿌려줄 예정
        HOST = default_ip + str(i)
        if floor == 'B1':
            if zone == 'apartment':
                if i == 17 or i == 18:
                    continue
                if i > 9: led_num = str(i)
                else: led_num = '0' + str(i)
                state[i] = get_free(floor, state, i, total_state, led_num)
                # state[i]['normal'] = total_state[f'B1-{led_num}']['normal']['free'] + total_state[f'B1-{led_num}']['wash']['free']
                # state[i]['compact'] = total_state[f'B1-{led_num}']['compact']['free']
                # state[i]['handicap'] = total_state[f'B1-{led_num}']['handicap']['free']
                # state[i]['electric'] = total_state[f'B1-{led_num}']['electric']['free']
                # state[i]['double'] = total_state[f'B1-{led_num}']['doubleParking']['free']
            elif zone == 'officetel':
                if i == 17 or i == 18:
                    led_num = str(i)
                    state[i] = get_free(floor, state, i, total_state, led_num)
                    # state[i]['normal'] = total_state[f'B1-{led_num}']['normal']['free'] + total_state[f'B1-{led_num}']['wash']['free']
                    # state[i]['compact'] = total_state[f'B1-{led_num}']['compact']['free']
                    # state[i]['handicap'] = total_state[f'B1-{led_num}']['handicap']['free']
                    # state[i]['electric'] = total_state[f'B1-{led_num}']['electric']['free']
                    # state[i]['double'] = total_state[f'B1-{led_num}']['doubleParking']['free']
                else:
                    continue
            elif zone == 'store':
                continue
                
        elif floor == 'B2':
            if zone == 'apartment':
                if i == 14 or i == 15:
                    continue
                if i > 9: led_num = str(i)
                else: led_num = '0' + str(i)
                state[i] = get_free(floor, state, i, total_state, led_num)
                # state[i]['normal'] = total_state[f'B2-{led_num}']['normal']['free'] + total_state[f'B2-{led_num}']['wash']['free']
                # state[i]['compact'] = total_state[f'B2-{led_num}']['compact']['free']
                # state[i]['handicap'] = total_state[f'B2-{led_num}']['handicap']['free']
                # state[i]['electric'] = total_state[f'B2-{led_num}']['electric']['free']
                # state[i]['double'] = total_state[f'B2-{led_num}']['doubleParking']['free']
            
            elif zone == 'officetel':
                if i == 14 or i == 15:
                    led_num = str(i)
                    state[i] = get_free(floor, state, i, total_state, led_num)
                    # state[i]['normal'] = total_state[f'B2-{led_num}']['normal']['free'] + total_state[f'B2-{led_num}']['wash']['free']
                    # state[i]['compact'] = total_state[f'B2-{led_num}']['compact']['free']
                    # state[i]['handicap'] = total_state[f'B2-{led_num}']['handicap']['free']
                    # state[i]['electric'] = total_state[f'B2-{led_num}']['electric']['free']
                    # state[i]['double'] = total_state[f'B2-{led_num}']['doubleParking']['free']
                else:
                    continue

        message = protocol_message(state[i], 60, 'none', version)
        client_thread = threading.Thread(target=handle_client, args=(HOST, message, test_case))
        client_thread.start()

    if floor == 'B1':  # 100cm, 160cm 전광판
        if zone == 'apartment':
            for k in range(21, 27):
                if k == 22 or k == 24 or k == 25:
                    continue

                states = data_sort_100cm(floor, k, zone_state)
                HOST = default_ip + str(k)
                message = protocol_message(states, 100, 'none', version)
                client_thread = threading.Thread(target=handle_client, args=(HOST, message, test_case))
                client_thread.start()

            for ip in range(31, 34):
                states = data_sort_160cm(ip, zone_state)
                HOST = default_ip + str(ip)
                message = protocol_message(states, 160, 'none', version)
                client_thread = threading.Thread(target=handle_client, args=(HOST, message, test_case))
                client_thread.start()

        elif zone == 'officetel':
            states = data_sort_100cm(floor, 27, zone_state)
            HOST = default_ip + str(27)
            message = protocol_message(states, 100, 'none', version)

            client_thread = threading.Thread(target=handle_client, args=(HOST, message, test_case))
            client_thread.start()

            states = data_sort_160cm(34, zone_state)
            HOST = default_ip + str(34)
            message = protocol_message(states, 160, 'none', version)

            client_thread = threading.Thread(target=handle_client, args=(HOST, message, test_case))
            client_thread.start()

        elif zone == 'store':
            states = data_sort_100cm(floor, 24, zone_state)
            HOST1 = '192.168.20.224'
            message = protocol_message(states, 100, 'store', version)

            client_thread = threading.Thread(target=handle_client, args=(HOST1, message, test_case))
            client_thread.start()

            states = data_sort_160cm(35, zone_state)
            HOST2 = '192.168.20.235'
            message = protocol_message(states, 160, 'store', version)

            client_thread = threading.Thread(target=handle_client, args=(HOST2, message, test_case))
            client_thread.start()

    if floor == 'B2':
        if zone == 'apartment':
            for k in range(21, 27):
                states = data_sort_100cm(floor, k, zone_state)
                HOST = default_ip + str(k)
                message = protocol_message(states, 100, 'none', version)
                client_thread = threading.Thread(target=handle_client, args=(HOST, message, test_case))
                client_thread.start()

        elif zone == 'officetel':
            states = data_sort_100cm(floor, 27, zone_state)
            HOST = default_ip + str(27)
            message = protocol_message(states, 100, 'none', version)
            client_thread = threading.Thread(target=handle_client, args=(HOST, message, test_case))
            client_thread.start()

def get_free(floor, state, i, total_state, led_num):
    state[i]['normal'] = total_state[f'{floor}-{led_num}']['normal']['free'] + total_state[f'{floor}-{led_num}']['wash']['free']
    state[i]['compact'] = total_state[f'{floor}-{led_num}']['compact']['free']
    state[i]['handicap'] = total_state[f'{floor}-{led_num}']['handicap']['free']
    state[i]['electric'] = total_state[f'{floor}-{led_num}']['electric']['free']
    state[i]['double'] = total_state[f'{floor}-{led_num}']['doubleParking']['free']

    return state[i]
            
def data_sort_100cm(floor, ip, total_state):
    if floor == 'B1':
        if ip == 24:  # 수변상가 100cm
            states = {'normal': total_state['store']['B1']['normal']['free'], 'operation': total_state['store']['B1']['operation']['free'],
                  'handicap': total_state['store']['B1']['handicap']['free'], 'compact': total_state['store']['B1']['compact']['free']}
        elif ip == 27:  # 오피스텔 100cm
            states = {'normal': total_state['officetel']['B1']['normal']['free'], 'electric': total_state['officetel']['B1']['electric']['free'],
                  'handicap': total_state['officetel']['B1']['handicap']['free'], 'compact': total_state['officetel']['B1']['compact']['free'], 
                  'double': total_state['officetel']['B1']['doubleParking']['free']}
        else:  # 아파트 100cm
            states = {'normal': total_state['apartment']['B1']['normal']['free'], 'electric': total_state['apartment']['B1']['electric']['free'],
                  'handicap': total_state['apartment']['B1']['handicap']['free'], 'compact': total_state['apartment']['B1']['compact']['free'], 
                  'double': total_state['apartment']['B1']['doubleParking']['free']}
    
    if floor == 'B2':
        if ip == 27:  # 오피스텔 100cm
            states = {'normal': total_state['officetel']['B2']['normal']['free'], 'electric': total_state['officetel']['B2']['electric']['free'],
                  'handicap': total_state['officetel']['B2']['handicap']['free'], 'compact': total_state['officetel']['B2']['compact']['free'], 
                  'double': total_state['officetel']['B2']['doubleParking']['free']}
        else:  # 아파트 100cm
            states = {'normal': total_state['apartment']['B2']['normal']['free'], 'electric': total_state['apartment']['B2']['electric']['free'],
                  'handicap': total_state['apartment']['B2']['handicap']['free'], 'compact': total_state['apartment']['B2']['compact']['free'], 
                  'double': total_state['apartment']['B2']['doubleParking']['free']}

    return states

def data_sort_160cm(ip, total_state):
    if ip == 34:  # 오피스텔 160cm
        states = {'normal': total_state['officetel']['B1']['normal']['free'] + total_state['officetel']['B2']['normal']['free'],
                 'electric': total_state['officetel']['B1']['electric']['free'] + total_state['officetel']['B2']['electric']['free'],
                  'handicap': total_state['officetel']['B1']['handicap']['free'] + total_state['officetel']['B2']['handicap']['free'], 
                  'compact': total_state['officetel']['B1']['compact']['free'] + total_state['officetel']['B2']['compact']['free'], 
                  'double': total_state['officetel']['B1']['doubleParking']['free'] + total_state['officetel']['B2']['doubleParking']['free']}

    elif ip == 35:  # 수변 상가 160cm
        states = {'normal': total_state['store']['B1']['normal']['free'], 'operation': total_state['store']['B1']['operation']['free'],
                  'handicap': total_state['store']['B1']['handicap']['free'], 'compact': total_state['store']['B1']['compact']['free']}

    else:  # 나머지 160cm 전광판의 경우 주차면 타입별로 B1 + B2를 하여 전체값을 구함
        states = {'normal': total_state['apartment']['B1']['normal']['free'] + total_state['apartment']['B2']['normal']['free'],
                 'electric': total_state['apartment']['B1']['electric']['free'] + total_state['apartment']['B2']['electric']['free'],
                  'handicap': total_state['apartment']['B1']['handicap']['free'] + total_state['apartment']['B2']['handicap']['free'], 
                  'compact': total_state['apartment']['B1']['compact']['free'] + total_state['apartment']['B2']['compact']['free'], 
                  'double': total_state['apartment']['B1']['doubleParking']['free'] + total_state['apartment']['B2']['doubleParking']['free']}

    return states
    
def socket_connect(host, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, 5000))
            s.sendall(message.encode(encoding='euc-kr'))  # 한글 표출이 필요할 경우 encoding='euc-kr' 추가
            data = s.recv(1024)                    # recv 활성화 할 경우 오류가 발생할 때가 있음
            s.close()
            LOGGER.info(f"{host} Received {data!r}")
        except ConnectionResetError as e:
            LOGGER.info(f"{e} - {host}")
        except ConnectionRefusedError as e:
            LOGGER.info(f"{e} - {host}")

def handle_client(host, message, test):
    if test == True:  # 테스트 시 로그만 출력
        if len(message) != 3:
            LOGGER.info(f"{host} SendAll {message}")
        else:
            for i in range(len(message)):
                LOGGER.info(f"{host} SendAll {message[i]}")
                time.sleep(2)
    else:
        if len(message) != 3:
            socket_connect(host, message)
            
        else:
            for i in range(len(message)):
                socket_connect(host, message[i])
                time.sleep(2)

def test_msg():
    # msg = '![000/U010/C6장애인면/U011/U010/C6장애인면/U011     20          20     !]'
    # msg = '![000/U010/C6장애인면/U011     20     /U010/C6장애인면/U011     20     !]'
    msg = '![000테스트!]'
    socket_connect('192.168.202.2', 5000, msg)

site = "ansan-grancity-xi"
zone = 'apartment' # apartment, officetel, store

# test_msg()
# total_count(site=site, zone=zone)
while(True):
    total_count(site=site, zone=zone)
    time.sleep(6)
