import numpy as np
from cal_similarity import cal_similarity

def update_ID(combined_center, kalman_input, p_prediction, P, update_check, simil_thr=300, nupdated = 10):
    """ID에 대한 정보들을 추가, 삭제, update하는 함수
    Args:
        combined_center     (ndarray): 합쳐진 contour의 중점 좌표들 (예: [[x1, y1], [x2, y2]])
        kalman_input        (ndarray): 추적중인 중점 좌표들 (예: [[x1, y1], [x2, y2]])
        p_prediction        (ndarray): 추적중인 중점 좌표들의 추정값(예: [[x1좌표, x1속도, y1좌표, y1속도], [x2좌표, x2속도, y2좌표, y2속도]])
        P                   (ndarray): 추적중인 중점 좌표들의 공분산(예: [np.shape(4,4), np.shape(4,4)])
        update_check            (int): 업데이트가 안된 횟수
        similarity              (int): 두 점이 가깝다 판단의 조건
        nupdated                (int): nupdated 동안 update되지 않으면 추적 끊기
    
    Results:
        kalman_input        (ndarray): 추가, 삭제, update된 추적중인 중점 좌표들
        p_prediction        (ndarray): 추가, 삭제, update된 추적중인 중점 좌표들의 추정값  
        P                   (ndarray): 추가, 삭제, update된 추적중인 중점 좌표들의 공분산
        update_check            (int): 업데이트가 안된 횟수
    """
    # for each inputs
    for lp_index, live_p in enumerate(combined_center):
        check_bool = False
        compare_similarity = []
        # if there is no tracking : new object appear
        if not kalman_input:
            kalman_input.append([live_p[0], live_p[1]])
            p_prediction.append([live_p[0], 0, live_p[1], 0])
            P.append(100 * np.eye(4))
            update_check.append(0)
        else:
            # compare the similarity with the existing object
            for kp_index, kalman_p in enumerate(kalman_input):
                similarity = cal_similarity(live_p, kalman_p)
                if similarity < simil_thr:
                    compare_similarity.append([kp_index, similarity])
            # recognize that the nearest point is the same object
            if compare_similarity:
                smallest_k = min(compare_similarity, key=lambda x : x[1])[0]
                kalman_input[smallest_k][0] = combined_center[lp_index][0]
                kalman_input[smallest_k][1] = combined_center[lp_index][1]
                update_check[smallest_k] = 0
                check_bool = True
            # if there is no near point : new object appear
            if check_bool == False:
                kalman_input.append([live_p[0], live_p[1]])
                p_prediction.append([live_p[0], 0, live_p[1], 0])
                P.append(100 * np.eye(4))
                update_check.append(0)

    # check if point has no update for 10 frame
    for i, _ in enumerate(kalman_input):
        update_check[i] += 1
        if update_check[i] > nupdated:
            kalman_input.pop(i)
            p_prediction.pop(i)
            P.pop(i)
            update_check.pop(i)
    
    return kalman_input, p_prediction, P, update_check