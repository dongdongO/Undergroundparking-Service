from pathlib import Path
import numpy as np
import torch
import torch.backends.cudnn as cudnn
from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.general import (check_file, check_img_size, check_imshow, check_requirements, increment_path, non_max_suppression, scale_coords)
from utils.plots import Annotator
from utils.torch_utils import select_device


class Detector:
    """사물인식을 위한 모델 초기 설정 및 로딩
    Attributes:
        opt   (namespace): 프로세스 실행 매개변수 및 설정값
        save_dir    (str): 영상분석 실행결과 저장 경로
        device      (str): CUDA를 사용할 GPU device 번호 (0번부터)
        model (:obj:`DetectMultiBackend`): Yolov5 모델의 프레임워크 (PyTorch, TensorFlow 등) 및 계층 구조 정보를 포함하는 객체
        stride, names, pt, jit, onnx, engine (Attributes of :obj: model): model 객체의 속성
        imgsz      (list): 전처리한 이미지 크기가 stride의 배수인지 확인
        half       (bool): 32비트 부동소수점 대신 16비트의 부동소수점 데이터 타입으로 연산 (PyTorch 프레임워크 모델 사용 및 CUDA 활성화 필수)
        view_img   (bool): 이미지 출력 가능한 환경인지 확인

    """
    def __init__(self, opt):
        check_requirements(exclude=('tensorboard', 'thop'))
        self.opt = opt

        # Directories
        self.save_dir = increment_path(Path(self.opt.project) / self.opt.name, exist_ok=self.opt.exist_ok)  # increment run
        (self.save_dir / 'labels' if self.opt.save_txt else self.save_dir).mkdir(parents=True, exist_ok=True)  # make dir

        # Load model
        self.device = select_device(self.opt.device)
        self.model = DetectMultiBackend(self.opt.weights, device=self.device, dnn=self.opt.dnn, data=self.opt.data)
        self.stride, self.names, self.pt, self.jit, self.onnx, self.engine = self.model.stride, self.model.names, self.model.pt, self.model.jit, self.model.onnx, self.model.engine
        self.imgsz = check_img_size(self.opt.imgsz, s=self.stride)  # check image size

        # Half
        self.opt.half &= (self.pt or self.jit or self.engine) and self.device.type != 'cpu'  # half precision only supported by PyTorch on CUDA
        if self.pt or self.jit:
            self.model.model.half() if self.opt.half else self.model.model.float()

        # Dataloader
        self.view_img = check_imshow()
        cudnn.benchmark = True

    @staticmethod
    def source_check_file(source):
        return check_file(source)

    def model_warmup(self, bs):
        self.model.warmup(imgsz=(bs, 3, *self.imgsz))  # warmup

    def __make_img(self, frame, webcam):
        """이미지 전처리
        입력 이미지(영상 프레임)의 색상을 RGB로 변환하고 그 값을 정규화
        Args:
            frame (ndarray): 입력 이미지 데이터
            webcam   (bool): 입력 데이터가 영상인지 이미지인지 판단

        Returns:
            ndarray: 전처리된 이미지 데이터
        """
        if webcam:
            img = [letterbox(x, self.imgsz, stride=self.stride, auto=self.pt)[0] for x in [frame]]  # Letterbox
            img = np.stack(img, 0)  # Stack
            img = img[..., ::-1].transpose((0, 3, 1, 2))  # Convert :: BGR to RGB, BHWC to BCHW
            img = np.ascontiguousarray(img)
        else:
            img = letterbox(frame, self.imgsz, stride=self.stride, auto=self.pt)[0]  # Padded resize
            img = img.transpose((2, 0, 1))[::-1]  # Convert :: HWC to CHW, BGR to RGB
            img = np.ascontiguousarray(img)

        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.opt.half else img.float()  # uint8 to fp16/32
        img /= 255  # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None]  # expand for batch dim

        return img

    def detect(self, frame, webcam):
        """사물 인식
        전처리된 이미지에서 사물을 검출하고 그 결과를 이미지에 표시
        Args:
            frame (ndarray): 입력 이미지 데이터
            webcam   (bool): 입력 데이터가 영상인지 이미지인지 판단

        Returns:
            list: 클래스(사물 이름) 및 box 좌표 (xyxy)가 포함된 리스트
            :obj:`Annotator`: box 표시 속성이 포함된 객체
            bool: 이미지 결과 표시 가능 여부 판단 결과 (True: 가능, False: 불가능)

        Examples:
            >>> detector.detect(frame, webcam)
        """
        bbox = list()
        im = self.__make_img(frame.copy(), webcam)

        # Inference
        pred = self.model(im, augment=self.opt.augment, visualize=self.opt.visualize)

        # NMS
        pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, self.opt.classes, self.opt.agnostic_nms, max_det=self.opt.max_det)

        # Second-stage classifier (optional)
        # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)

        # Process predictions
        for i, det in enumerate(pred):  # per image
            im0 = frame.copy()
            annotator = Annotator(im0, line_width=self.opt.line_thickness, example=str(self.names))

            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                for *xyxy, conf, cls in reversed(det):
                    label = self.names[int(cls)]
                    bbox.append({'label': label, 'box': [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])]})
                    annotator.box_label(xyxy, label, color=(0, 0, 255))

        return bbox, annotator, self.view_img
