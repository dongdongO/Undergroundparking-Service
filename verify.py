'''
In runfinal.py line 138;
Make final_state which comes out more of 'free' or 'in'
Value num determine the number of votes 
'''
from utils.general import LOGGER


def verify(cam, cam_seq, state, num=5):
    if num % 2 == 0:  # 검증 결과가 동률이 나오는 것을 방지하기 위해 검증 횟수를 홀수 번으로 변경
        num -= 1

    state[cam_seq].append(list(cam['state'].values()))  # 각 카메라 별 주차 상태 리스트 요소 추가
    # 개수가 num개 넘어가면 가장 오래된 거 삭제
    if len(state[cam_seq]) > num:
        state[cam_seq].popleft()
    # LOGGER.info(f'{cam_seq} - Verifying parking state : {state[cam_seq]}')

    if len(state[cam_seq]) == num:  # 동일 카메라에 대해 num번 영상분석을 수행했을 때
        verify_state = [list() * len(cam['state']) for x in range(len(cam['state']))]
        for i in range(len(state[cam_seq][0])):  # 각 주차면 별 주차 상태를 리스트(verify_state)로 저장
            for j in range(num):
                verify_state[i].append(state[cam_seq][j][i])

        final_state = dict()  # 최종 주차 상태를 저장하는 리스트 초기화
        for i, states in enumerate(verify_state):  # 각 주차면 별 주차 상태 리스트에서 최종 주차 상태를 다수결로 결정
            if verify_state[i].count('free') > verify_state[i].count('in'):
                final_state[cam['pos'][i]] = 'free'
            else:
                final_state[cam['pos'][i]] = 'in'

        LOGGER.info(f'{cam_seq} - Final Parking State: {final_state}')
        return final_state

    else:
        return None
