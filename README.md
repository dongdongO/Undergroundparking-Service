# 안양2차 SKV1 영상분석 소스코드 사용법
본 소스코드는 ultralytics의 yolov5 소스(https://github.com/ultralytics/yolov5)를 기반으로 작성되었으며 
여기서는 yolov5 소스 외 추가된 파일에 대해서만 설명, 소스코드에 대한 자세한 설명은 영상분석 인수인계서 참조
1. `config_Anyang2_SKV1(_vpn).yaml`
- 주차면 점유 판단에 필요한 각종 정보를 포함하는 설정 파일
- 파일명 끝에 `_vpn`이 추가된 파일은 VPN Proxy 접속 주소 기준
  - `src`: 영상의 RTSP 스트리밍 접속 주소
  - `pos`: 영상 내 점유 판단을 할 주차면의 slot id 리스트
  - `uuid`: 영상 내 점유 판단을 할 주차면의 uuid 리스트
  - `roi`: 주차면의 직사각형 관심 영역 (Region of Interest; ROI) 리스트, 실내 주차장에서 사용
  - `double_roi`: 이중주차가 발생하는 위치의 ROI 리스트
  - `double_slots`: 이중주차로 영향을 받는 기존 주차면들의 slot id 리스트
2. `check_state.py`
- 주차면 점유 여부를 판단하는 알고리즘 소스 코드
  - `inout`: 인식된 차량의 bounding box와 설정한 ROI를 이용하여 점유 여부를 판단하는 함수
3. `dataloader.py`
- 카메라 영상을 읽고 그 영상을 Yolov5 모델에 전달하는 소스코드
4. `detector.py`
- 영상분석을 위한 Yolov5 모델의 매개변수 값을 설정하고, 
이미지 전처리 (preprocessing) 후 분석 결과를 bounding box 또는 선분으로 이미지 상에 표시하는 소스코드
5. `find_ROI.py`
- ROI 설정을 위한 소스 코드
6. `run_final.py`
- 영상분석 서비스를 실행하는 메인 소스코드
7. `transmit_server.py`
- 영상분석으로 얻은 주차면 점유 결과를 주차면 현황 API 서버로 전송하는 소스코드
  - `sendstate2server`
    - 주차면 점유 상태를 주차면 현황 API 서버로 전송하는 함수
    - API 서버 주소 뒤에 각 주차면의 uuid를 추가하여 각 주차면 별 데이터를 호출한 후, 
    주차면 현황을 알려주는 ‘slot_status’ 키 값에 주차면 점유 현황 값 (‘in’, ‘free’)을 전송
8. `myyolo_v2.pt`
- 영상분석에 사용되는 yolov5의 모델 가중치 파일, 해당 모델은 차량만을 인식할 수 있도록 별도로 학습된 모델
9. `verify.py`
- 여러 번 영상분석을 수행 중 동일한 주차 상황임에도 불구하고 일부 차량을 미인식하는 경우 대응하는 소스코드
- 동일한 카메라에 대해 여러 번 영상분석을 반복한 후, 각 주차면 별로 점유 현황을 취합하여 최종 주차 상태를 다수결로 결정하는 알고리즘

## 사용법
1. 영상분석 실행 전 다음 명령 수행을 통해 실행에 필요한 필수 패키지 설치, 
패키지 설치 전 3.7 버전 이상의 Python 실행 모듈 및 1.7 버전 이상의 PyTorch 패키지 설치 여부 확인, 
PyTorch 설치 방법은 https://pytorch.org/get-started/locally/ 참고
```
$ cd anyang_skv1_inout
$ pip install -r requirements.txt
```
2. `run_final.py` 파일 실행
- 실행 변수에 대한 설명은 `run_final.py` 내의 `parse_opt` 함수 참고
- Anaconda 가상환경 사용 시 설치된 가상환경 활성화 필요
```
$ conda activate inout
$ python3 run_final.py --weights yolov5_custom_v2.pt --conf 0.15 --iou 0.5 --device 0 --nosave --exist --line 1
```
### 자동 실행 스크립트를 이용한 실행
1. 실제 서비스 제공을 위해 본 프로세스를 실행하기 위해서는 crontab (Linux)에 실행 스크립트 파일(`runCheck.sh`)을 작성하여 실행가능
2. crontab에 해당 스크립트를 자동 실행하기 위해 터미널에 다음과 같이 입력
```
$ crontab -e
```
3. 최초 crontab 편집 시 터미널 내에서 사용할 텍스트 편집기를 선택 (GNU Nano / Vim / 기타 중 택 1)\
(각 텍스트 편집기에 대한 사용법은 구글 검색)
4. crontab 편집 창 맨 아랫줄에 다음 구문 추가
```
* * * * *        bash ~/runCheck.sh
```
- 스크립트 파일의 실행 경로에 따라 변경 가능
5. 실행 스크립트 파일(`runCheck.sh`)의 주요 기능
   - 자정 기준으로 매 n시간 정각에 프로세스 종료 및 재기동하며 그 결과를 `run_restart.log`에 기록
```
if [ $nowMinutes -eq 0 ] && [ $nowHour -eq 0 ]; then
  pkill -9 -ef run_final
  echo "$DATE run hour Kill Success!" >> "$LOG_PATH"/run_restart.log
  sleep 1;
fi
```
- 프로세스를 실행하기 위해 conda 가상환경 활성화 (Anaconda 사용시) 및 실행 경로 설정
  - 실행 결과 로그 파일을 저장하기 위한 경로 설정
  - 영상분석 프로세스를 실행 옵션을 설정한 후 프로세스의 실행 과정을 `run_debug-XXXX.log`(XXXX: HHMM, 시분)에 기록
  - 프로세스가 정상적으로 실행중인지 확인한 후 그 결과를 `run_restart.log`에 기록
```
PYTHON_CHECK_1=`ps -ef | grep -v "grep" | grep "python3 ./run_final" | wc -l`
if [ "$PYTHON_CHECK_1" -lt 1 ]; then
       conda activate inout && cd ~/anyang_skv1_inout
       mkdir -p "$LOG_PATH"/debug/$(date "+%Y-%m-%d")
       nohup python3 ./run_final.py --weights yolov5_custom_v2.pt --data data.yaml --conf-thres 0.15 --iou 0.5 --line 1 --device 0 --nosave --exist --service --send-mqtt > "$LOG_PATH"/debug/$(date "+%Y-%m-%d")/run_debug_1-$(date "+%H%M").log 2>&1 &
       sleep 5;
       PYTHON_CHECK_1=`ps -ef | grep -v "grep" | grep "python3 ./run_final" | wc -l`
       if [ "$PYTHON_CHECK_1" -lt 1 ]; then
               echo "$DATE run Process Restart Failed!" >> "$LOG_PATH"/run_restart.log
       else
               echo "$DATE run Process Restart Success!" >> "$LOG_PATH"/run_restart.log
       fi
else
        echo "$DATE run Process Alive" >> /"$LOG_PATH"/run_alive.log
fi
```