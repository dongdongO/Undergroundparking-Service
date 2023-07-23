
# Underground-Parking-Service
- This project is to make parkinglot service using camera. 이것은 센서로 주차상황을 파악하는 것과는 다르게 이중주차의 상태까지 판단이 가능하게 한다
- Detection
    - Object detection by yolov5
    - Tracking by opencv
- 데이터 전송
    - Mqtt


## Result
- 주차장 사진 & tracking gif 영상

# Tested Environment
## Computer Server
- Linux & Vi editor
    - Intel Core i7-6700 @ 3.4GHz + NVIDIA GeForce GTX 2060 * 3
    - 하나의 서버당 200개가 넘는 카메라 담당

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
    - use camera via gstreamer on Jetson: jetson
        - ./main jetson
```

- Mouse Drag: Change top view angle
- Keyboard (asdwzx) : Change top view position


# How to build a project
## 0. Requirements
- OpenCV 4.x
- CMake
- TensorRT 8.0.x
    - If you get build error related to TensorRT, modify cmake settings for it in `inference_helper/inference_helper/CMakeLists.txt`

## 1. Download source code and pre-built libraries 
- Download source code
    - If you use Windows, you can use Git Bash
    ```sh
    git clone https://github.com/iwatake2222/self-driving-ish_computer_vision_system.git
    cd self-driving-ish_computer_vision_system
    git submodule update --init
    sh inference_helper/third_party/download_prebuilt_libraries.sh
    ```
- Download models
    ```sh
    sh ./download_resource.sh
    ```

## 2-a. Build in Windows (Visual Studio)
- Configure and Generate a new project using cmake-gui for Visual Studio 2019 64-bit
    - `Where is the source code` : path-to-cloned-folder
    - `Where to build the binaries` : path-to-build	(any)
- Open `main.sln`
- Set `main` project as a startup project, then build and run!
- Note:
    - You may need to modify cmake setting for TensorRT for your environment

## 2-b. Build in Linux (Jetson Xavier NX)
```sh
mkdir build && cd build
# cmake .. -DENABLE_TENSORRT=off
cmake .. -DENABLE_TENSORRT=on
make
./main
```

# Note
## cmake options
```sh
cmake .. -DENABLE_TENSORRT=off  # Use TensorFlow Lite (default)
cmake .. -DENABLE_TENSORRT=on   # Use TensorRT

cmake .. -DENABLE_SEGMENTATION=on    # Enable Road Segmentation function (default)
cmake .. -DENABLE_SEGMENTATION=off   # Disable Road Segmentation function

cmake .. -DENABLE_DEPTH=on    # Enable Depth Estimation function (default)
cmake .. -DENABLE_DEPTH=off   # Disable Depth Estimation function
```

## Misc
- It will take very long time when you execute the app for the first time, due to model conversion
    - I took 80 minutes with RTX 3060ti
    - I took 10 - 20 minutes with GTX 1070

# Software Design
## Class Diagram
![class_diagram](00_doc/class_diagram.jpg)

## Data Flow Diagram
![data_flow_diagram](00_doc/data_flow_diagram.jpg)

# Model Information
## Details
- Object Detection
    - YOLOX-Nano, 480x640
    - https://github.com/PINTO0309/PINTO_model_zoo/blob/main/132_YOLOX/download_nano_new.sh
    - https://github.com/PINTO0309/PINTO_model_zoo/blob/main/132_YOLOX/download_nano.sh
- Lane Detection
    - Ultra-Fast-Lane-Detection, 288x800
    - https://github.com/PINTO0309/PINTO_model_zoo/blob/main/140_Ultra-Fast-Lane-Detection/download_culane.sh
- Road Segmentation
    - road-segmentation-adas-0001, 512x896
    - https://github.com/PINTO0309/PINTO_model_zoo/blob/main/136_road-segmentation-adas-0001/download.sh
- Depth Estimation
    - LapDepth, 192x320
    - https://github.com/PINTO0309/PINTO_model_zoo/blob/main/148_LapDepth/download_ldrn_kitti_resnext101.sh
    - LapDepth, 256x512
    - [00_doc/pytorch_pkl_2_onnx_LapDepth.ipynb](00_doc/pytorch_pkl_2_onnx_LapDepth.ipynb)

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

