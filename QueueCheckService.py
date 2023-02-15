from collections import deque
from copy import deepcopy
import datetime
import cv2
import base64


class QueueCheckService:
    def __init__(self):
        self.totalCCTVSlotDict = dict()
        self.cam = 0
        self.result = 0
        self.previous_state = dict()
        self.previous_img = dict()

    def setterCam(self, cam_param):
        self.cam = deepcopy(cam_param)

    def setterResult(self, result_param):
        self.result = deepcopy(result_param)
        self.result['img-base64'] = str()

    def getterCam(self):
        return self.cam

    def getterResult(self):
        return self.result

    def returnExampleDict(self):
        self.totalCCTVSlotDict = {
            "1-2-3-4": dict(),
            "5-6-7-8": dict()
        }

    def returnExampleCam(self):
        self.cam = {
            'pos': ['123', '456', '789'],
            'state': ['free', 'in', 'free']
        }
        return self.cam

    def checkCCTVId(self, cctvId):
        if cctvId not in self.totalCCTVSlotDict.keys():
            self.totalCCTVSlotDict[cctvId] = dict()
            self.previous_state[cctvId] = dict()
            self.previous_img[cctvId] = str()

    def writeLog(self):
        with open("/home/ves/anyang_parking_inout/yjTestLog.txt", "a") as logTxt:
            logTxt.write(str(datetime.datetime.now()) + ":" + str(self.totalCCTVSlotDict) + "\n")
            logTxt.close()

    def queueCheckService(self, seq, queue_size):  # cam = cam, seq = cam_seq
        cam = self.cam
        pos = cam['pos']  # ['sdf','sdf']
        status = cam['state']  # {"1-x1-y1-1" : "in", ... }

        idx_list = [i for i in range(len(pos))]
        new_status = list()
        for idx, slot, st in zip(idx_list, pos, status.values()):
            if slot not in self.totalCCTVSlotDict[seq]:
                self.totalCCTVSlotDict[seq][slot] = deque([])
                self.previous_state[seq][slot] = cam['state'][slot]
            if len(self.totalCCTVSlotDict[seq][slot]) >= queue_size:
                deque.popleft(self.totalCCTVSlotDict[seq][slot])
            self.totalCCTVSlotDict[seq][slot].append(st)

            if all(d == self.totalCCTVSlotDict[seq][slot][0] for d in self.totalCCTVSlotDict[seq][slot]):
                if self.totalCCTVSlotDict[seq][slot][0] == 'free':
                    cam['state'][slot] = 'free'
                    self.previous_state[seq][slot] = 'free'
                else:
                    cam['state'][slot] = 'in'
                    self.previous_state[seq][slot] = 'in'
            else:
                cam['state'][slot] = self.previous_state[seq][slot]

        self.result['predicted-by-model-list-v2'] = list(cam['state'].values())

        if "img-path" not in self.result.keys():
            if self.previous_img[seq]:
                self.result["img-path"] = self.previous_img[seq]
        else:
            if self.previous_img[seq]:
                self.result['img-changed'] = 1
            self.previous_img[seq] = self.result['img-path']

    def checkImg(self, seq, modelList, frame):
        self.result['predicted-by-model-list-v2'] = modelList
        if not self.result["img-path"]:
            if self.previous_img[seq]:
                self.result["img-path"] = self.previous_img[seq]
        else:
            if self.previous_img[seq]:
                self.result['img-changed'] = 1
            self.previous_img[seq] = self.result['img-path']

            retval, buffer = cv2.imencode(".jpg", frame)
            jpg_as_text = base64.b64encode(buffer)
            self.result['img-base64'] = jpg_as_text

    def insertModelList(self, modelList):
        self.result['predicted-by-model-list-v1'] = modelList
