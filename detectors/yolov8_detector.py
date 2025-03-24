# detectors/yolov8_detector.py
import cv2
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # Ensure you have the correct YOLOv8 model file

def detect_objects(frame):
    """
    Detects objects in a given frame using YOLOv8.
    Returns a list of detected objects with confidence scores and bounding boxes.
    """
    results = model(frame)
    detections = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()  # Bounding box coordinates
            confidence = float(box.conf[0])  # Confidence score
            class_name = model.names[int(box.cls[0])]  # Object class name

            detections.append({
                "label": class_name,
                "confidence": confidence,
                "bbox": [int(x1), int(y1), int(x2), int(y2)]
            })

    return detections
