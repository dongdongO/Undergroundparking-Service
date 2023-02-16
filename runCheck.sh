#!/bin/bash
minutes=`awk '{print $0/60;}' /proc/uptime`;
if [ $(echo "1 > $minutes" | bc) -ne 0 ]; then
  echo "$minutes";
  exit 0;
fi

export QT_DEBUG_PLUGINS=1
export PATH=/home/ves/anaconda3/bin:/home/ves/anaconda3/condabin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
source ~/anaconda3/etc/profile.d/conda.sh

SCRIPT=`realpath $0`
SCRIPT_PATH=`dirname $SCRIPT`
# 또는
#SCRIPT_PATH=$( cd "$(dirname "$0")" ; pwd )
DATE=$(date "+%Y-%m-%d_%H:%M:%S")
LOG_PATH="$SCRIPT_PATH/shellLog"

nowHour=$((10#`date +'%H'`%2));
nowMinutes=$((10#`date +'%M'`%60));
#nowMinutes=$((date +'%M') | bc);
if [ $nowMinutes -eq 0 ] && [ $nowHour -eq 0 ]; then
  pkill -9 -ef run_final
  echo "$DATE run hour Kill Success!" >> "$LOG_PATH"/run_restart.log
  sleep 1;
fi

PYTHON_CHECK_1=`ps -ef | grep -v "grep" | grep "python3 ./run_final" | wc -l`
if [ "$PYTHON_CHECK_1" -lt 1 ]; then 
        conda activate inout && cd ~/ansan_xi_inout
        mkdir -p "$LOG_PATH"/debug/$(date "+%Y-%m-%d")
        nohup python3 ./run_final.py --weights yolov5x.pt --data data.yaml --conf-thres 0.03 --iou 0.45 --line 1 --device 0 --nosave --exist --service > "$LOG_PATH"/debug/$(date "+%Y-%m-%d")/run_debug-$(date "+%H%M").log 2>&1 &
        sleep 5;
        PYTHON_CHECK_1=`ps -ef | grep -v "grep" | grep "python3 ./run_final" | wc -l`
        if [ "$PYTHON_CHECK_1" -lt 0 ]; then
                echo "$DATE run Process Restart Failed!" >> "$LOG_PATH"/run_restart.log
        else
                echo "$DATE run Process Restart Success!" >> "$LOG_PATH"/run_restart.log
        fi
else
        echo "$DATE run Process Alive" >> /"$LOG_PATH"/run_alive.log
fi
