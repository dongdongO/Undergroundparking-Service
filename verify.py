'''
Used in runfinal.py line 138
Make final_state which comes out more of 'free' or 'in'
Value num determine the number of votes 
'''
from utils.general import LOGGER


def verify(cam, cam_seq, state, num=5):
    if num % 2 == 0:  # to prevent ties
        num -= 1

    state[cam_seq].append(list(cam['state'].values()))  # add values for each camera
    # update new values
    if len(state[cam_seq]) > num:
        state[cam_seq].popleft()
    # LOGGER.info(f'{cam_seq} - Verifying parking state : {state[cam_seq]}')

    if len(state[cam_seq]) == num:  # when analysis is performed num times for the same camera
        verify_state = [list() * len(cam['state']) for x in range(len(cam['state']))]
        for i in range(len(state[cam_seq][0])):  # Save the parking status of each parking surface as a list(verify_state)
            for j in range(num):
                verify_state[i].append(state[cam_seq][j][i])

        final_state = dict()  # init final state 
        # Determine the final parking status in list(verify_state) for each parking surface by majority vote
        for i, states in enumerate(verify_state):
            if verify_state[i].count('free') > verify_state[i].count('in'):
                final_state[cam['pos'][i]] = 'free'
            else:
                final_state[cam['pos'][i]] = 'in'

        LOGGER.info(f'{cam_seq} - Final Parking State: {final_state}')
        return final_state

    else:
        return None
