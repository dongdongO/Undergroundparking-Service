import numpy as np

def kalmanFilter_(measuredstate, estimation, letterP, dt=1):
    
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