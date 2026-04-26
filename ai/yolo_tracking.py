# YOLOV8 based tracking module for AIZeeBot
from ultralytics import YOLO
from robot.motor_control import move, stop
import cv2

model = YOLO("ai/models/yolov8n.pt")

def run_tracking():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        results = model(frame)

        found = False

        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 0:
                    found = True
                    move("forward")
                    break

        if not found:
            stop()