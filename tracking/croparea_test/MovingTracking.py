import cv2
import numpy as np
from math import sqrt
from collections import deque
from kalmanFilter import *
from framecrop import *

class MovingTracking:
    def __init__(self):
        #init  
        self.MinArea=200
        
        self.Green = (0,255,0)
        self.Red = (0,0,255)
        self.Blue = (255,0,0)
        
        self.is_moving = False
        self.tracemoving_queue = deque(maxlen=150)
        
        self.x_esti = np.array([0,0,0,0]).transpose()
        self.P = 100 * np.eye(4)

    def detect_motion(self, frame_use, frame_output):
        _, threshold_frame = cv2.threshold(src=frame_use, thresh=30, maxval=255, type=cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(image=threshold_frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

        combined_center = combine_contour(contours, self.MinArea)

        if not combined_center:
            if self.is_moving == False:
                pass
            else:
                z_meas = np.array([self.node_x_old, self.node_y_old])
                self.x_esti, self.P = kalmanFilter_(z_meas, self.x_esti, self.P)

                cv2.circle(frame_output, (int(self.x_esti[0]),int(self.x_esti[2])), 10, self.Green, -1)
                cv2.circle(frame_output, (self.node_x_old, self.node_y_old), 10, self.Red, -1)
                self.tracemoving_queue.append((self.x_esti[0], self.x_esti[2]))
                # End condition
                if len(self.tracemoving_queue) > 149:
                    distance = sqrt((self.tracemoving_queue[0][0] - self.tracemoving_queue[-1][0])**2 + (self.tracemoving_queue[0][1] - self.tracemoving_queue[-1][1])**2)
                    if distance < 10:
                        self.tracemoving_queue.clear()
                        self.is_moving = False

        else:
            self.node_x = combined_center[0][0]
            self.node_y = combined_center[0][1]

            z_meas = np.array([self.node_x, self.node_y])
            self.x_esti, self.P = kalmanFilter_(z_meas, self.x_esti, self.P)
            self.node_x_old, self.node_y_old = self.node_x, self.node_y
            cv2.circle(frame_output, (int(self.x_esti[0]),int(self.x_esti[2])), 10, self.Green, -1)
            cv2.circle(frame_output, (self.node_x,self.node_y), 10, self.Red, -1)
            self.tracemoving_queue.append((self.x_esti[0], self.x_esti[2]))
            self.is_moving = True
            
        for _ in range(len(self.tracemoving_queue)):
            cv2.circle(frame_output, (int(self.tracemoving_queue[0][0]),int(self.tracemoving_queue[0][1])), 5, self.Blue, -1)
            self.tracemoving_queue.rotate(1)
        
        return frame_output