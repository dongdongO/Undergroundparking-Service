
import numpy as np

# dt값에 따라 filter의 정도가 달라진다. 다만 큰 차이는 없다
def kalmanFilter_(measuredstate, estimation, letterP, dt=1):
    """입력된 현재 좌표와 전의 추정값과 오차 공분산으로 다음 위치 예측
    Args:
        measuredstate   (ndarray): 현재 추적중인 중점 좌표 (예: [x좌표, y좌표])
        estimation      (ndarray): 현재 추적중인 중점의 이전 추정값 ([x좌표, x속도, y좌표, y속도], init : [현재 x좌표, 0, 현재 y좌표, 0])
        letterP         (ndarray): 현재 추적중인 중점의 이전 공분산 (init : 100 * np.eye(4), 자동 update)
        dt                (float): 
    
    Returns:
        renewed_e       (ndarray): 현재 추적중인 중점의 추정값 ([x좌표, x속도, y좌표, y속도], init : [현재 x좌표, 0, 현재 y좌표, 0])
        renewed_P       (ndarray): 현재 추적중인 중점의 공분산 (np.shape(4,4))
    """
    
    letterA = np.array([[1, dt, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, dt],
                        [0, 0, 0, 1]])
    
    letterQ = 0.01 * np.eye(4)
    
    letterH = np.array([[1, 0, 0, 0],
                        [0, 0, 1, 0]])
    
    letterR = np.array([[50, 0],
                        [0, 50]])
    
    # 1. 추정값과 오차 공분산 예측
    predicted_e = np.dot(letterA,estimation)
    predicted_P = np.dot(np.dot(letterA,letterP),np.transpose(letterA)) + 0.01*letterQ
    
    # 2. 칼만 이득 계산
    letterK = np.dot(np.dot(predicted_P,letterH.T),np.linalg.inv(np.dot(np.dot(letterH,predicted_P),np.transpose(letterH)) + letterR))
    
    # 3. 추정값 계산
    measurement = np.array([measuredstate[0], measuredstate[1]]).transpose()
    renewed_e = predicted_e + np.dot(letterK,(measurement - np.dot(letterH,predicted_e)))
    
    # 4. 오차 공분산 계산
    renewed_P = predicted_P - np.dot(np.dot(letterK,letterH),predicted_P)
    
    return renewed_e, renewed_P