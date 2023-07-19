import cv2
import torch
from sort import Sort

# Initialize the model
model = torch.hub.load('ultralytics/yolov5', 'yolov5m',
                            device='cuda:0' if torch.cuda.is_available() else 'cpu')
model.classes = [2] #자동차만

# Initialize the object tracker
tracker = Sort()

# Open the video
cap = cv2.VideoCapture("path/to/video.mp4")

while True:
    # Read the frame
    ret, frame = cap.read()
    if not ret:
        break

    # Perform object detection
    boxes, labels, scores = model.detect(frame)

    # Perform object tracking
    tracked_objects = tracker.track(boxes)

    # Draw bounding boxes around moving cars
    for obj in tracked_objects:
        if obj.label == "car" and obj.is_moving:
            cv2.rectangle(frame, (obj.xmin, obj.ymin), (obj.xmax, obj.ymax), (0, 255, 0), 2)

    # Show the frame
    cv2.imshow("Video", frame)
    if cv2.waitKey(1) == ord("q"):
        break

# Release the video
cap.release()
cv2.destroyAllWindows()