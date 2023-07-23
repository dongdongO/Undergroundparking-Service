
# Underground-Parking-Service
- This project is to make parkinglot service using camera. This makes it possible to determine the state of double parking, unlike determining the parking situation with a sensor.
- Detection
    - Object detection by yolov5
    - Tracking by opencv
- Data Transmission
    - Mqtt


## Result
![Alt text](runs/detect/exp/test_result.jpg)

# Tested Environment
## Computer Server
- Linux & Vi editor
    - Intel Core i7-6700 @ 3.4GHz + NVIDIA GeForce GTX 2060 * 3
    - Responsible for over 200 cameras per server

# Usage
```
./main [input]
 - input:
    - use the default image file set in source code (main.cpp): blank
        - ./main
     - use video file: *.mp4, *.avi, *.webm
        - ./main test.mp4
     - use image file: *.jpg, *.png, *.bmp
        - ./main test.jpg
    - use camera: number (e.g. 0, 1, 2, ...)
        - ./main 0
```

- check runCheck.sh
- Reboot every 2 hours


# Model Information
## Details
- Object Detection
    - YOLOv5
- OpenCV

## Performance
| Model                            | Jetson Xavier NX | GTX 1070 |
| -------------------------------- | ---------------: | -------: |
| == Inference time ==                                           |
|  Object Detection                |          10.6 ms |   6.4 ms |
|  Lane Detection                  |           9.6 ms |   4.9 ms |
|  Road Segmentation               |          29.1 ms |  13.5 ms |
|  Depth Estimation                |          55.2 ms |  37.8 ms |
| == FPS ==                                                      |
|  Total (All functions)           |          6.8 fps | 10.9 fps |
|  Total (w/o Segmentation, Depth) |         24.4 fps | 33.3 fps |

* Input
    - Jetson Xavier NX: Camera
    - GTX 1070: mp4 video
* With TensorRT FP16
* "Total" includes image read, pre/post process, other image process, result image drawing, etc.

# License


# Acknowledgements
I utilized the following OSS in this project. I appreciate your great works, thank you very much.

## Code, Library
- TensorFlow
    - https://github.com/tensorflow/tensorflow
    - Copyright 2019 The TensorFlow Authors
    - Licensed under the Apache License, Version 2.0
    - Generated pre-built library
- Pytorch
    - https://github.com/pytorch
    - Copyright (c) Soumith Chintala 2016, 
    - Licensed under the BSD 3-Clause License
    - Generated pre-built library

## Model

- YOLO v5
    - https://github.com/ultralytics/yolov5
    - Copyright (c) Megvii, Inc. and its affiliates. All Rights Reserved
    - Licensed under the GNU Affero General Public License v3.0

