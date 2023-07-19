import cv2
import time
import numpy as np
import glob

#불러올 영상 & 녹화할 영상 위치
capture = cv2.VideoCapture("./CCTV17_crop_1.mp4")
capture.set(cv2.CAP_PROP_POS_MSEC, 100)
output_path = './output_result.mp4'

#불러온 영상의 가로,세로,fps & 녹화할 영상 저장 형식
width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(capture.get(cv2.CAP_PROP_FPS))
codec = cv2.VideoWriter_fourcc(*'mp4v')

# 배경 추출을 위한 KNN,kernel 설정
bget_KNN = cv2.createBackgroundSubtractorKNN(detectShadows=False)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(1,1))

#init
time_cost = 0
time_check =0
fps_cost = 0
frame_num = 0
condition = ''
record = False

# 영상 frame 별로 처리
while True:
    key = cv2.waitKey(33)
    start = time.time()
    frame_num +=1 
    
    
    #ESC 누르면 종료됨
    if key == 27:
        break
    
    return_value, frame = capture.read()
    # 비디오 프레임 정보가 있으면 계속 진행 
    if return_value:
        pass
    else : 
        print('비디오가 끝났거나 오류가 있습니다')
        break
    
    # Gray로 바꿔주고 noise 제거를 위한 blur 처리 -> blur 처리가 오히려 객체 탐지에 방해되서 주석 처리
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.GaussianBlur(frame_gray,(3,3),0)

    # 배경 추출을 위한 KNN 적용
    backgroundsub_mask_KNN = bget_KNN.apply(frame_gray)
    backgroundsub_mask_KNN = cv2.morphologyEx(backgroundsub_mask_KNN,cv2.MORPH_OPEN, kernel)
    #backgroundsub_mask_KNN = cv2.morphologyEx(backgroundsub_mask_KNN,cv2.MORPH_CLOSE, kernel)
    backgroundsub_mask_KNN = np.stack((backgroundsub_mask_KNN,)*3, axis=-1)
    #bitwise_image_KNN = cv2.bitwise_and(frame, backgroundsub_mask_KNN)
    
    # 변화 정도를 구하기
    for_diff = cv2.cvtColor(backgroundsub_mask_KNN, cv2.COLOR_BGR2GRAY)
    diff_cnt = cv2.countNonZero(for_diff)
    #print(diff_cnt)
    #time.sleep(1)
    
    # 변화가 있으면 frame 전달 시작, 일정 시간 동안 변화 없으면 전달 중지
    # 첫 frame_num > 5 는 초반에 변화 정도가 급격하게 커서 급한대로 추가 -> 수정 필요
    # 기본적인 순환복잡도가 너무 높음 -> 수정 필요
    if(diff_cnt > 500):
        if record == True:
            condition = "move on and relay"
            #video.write(frame)
        else:
            condition = 'start'
            record = True
            #video = cv2.VideoWriter('output_result.mp4',codec, 20.0, (frame.shape[1], frame.shape[0]))
    else:
        if record == True:
            if time_check < 5000: # 시간조건
                condition = "no move but relay"
                #video.write(frame)
            else:
                condition = "end"
                record = False
                time_check = 0
                #video.release()
        else:
            condition = "not relay"
            pass

    #소요 시간 및 평균 FPS 구하기
    time_temp = 1000*(time.time()-start)  
    if time.time()-start != 0.0:
        fps_temp = 1/(time.time()-start)  
    else:
        fps_temp=0.01

    time_check += time_temp
    time_cost = time_cost + time_temp
    fps_cost = fps_cost + fps_temp
    #print('소요 시간 : {:.2f} ms \t 평균FPS : {:.2f}'.format(time_temp,fps_temp))
    
    #결과창 봉합해서 출력
    concat_image = np.concatenate((frame,backgroundsub_mask_KNN), axis=1)
    
    
    
    cv2.putText(concat_image, 'change : '+str(diff_cnt), (40, 480), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255))
    cv2.putText(concat_image, 'condition : '+ condition, (40, 530), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))

    cv2.imshow('result', concat_image)
    cv2.imshow('frame', frame)
    #cv2.imshow('backgroundsub_KNN', backgroundsub_mask_KNN)
    #cv2.imshow('bitwise_KNN', bitwise_image_KNN)
    #cv2.imshow('original', frame)
    

#메모리 반납
print('소요시간 평균 : {:.2f} ms\t 평균FPS : {:.2f}'.format(time_cost / frame_num, fps_cost/ frame_num))
capture.release()
cv2.destroyAllWindows()
