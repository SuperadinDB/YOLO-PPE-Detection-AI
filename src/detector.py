from pathlib import Path

import cv2
from ultralytics import YOLO


class PPEDetector:

    def __init__(self, model_path, confidence=0.25):
        self.model = YOLO(model_path)
        self.confidence = confidence

    def predict(self, frame):
        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            imgsz=640,
            device=0,
            verbose=False,
        )

        return results[0]

    def draw(self, frame, result):
        return result.plot()

    def get_detections(self, result):

        detections = {}

        if result.boxes is None or len(result.boxes) == 0:
            return detections

        # Transferimos TODO desde GPU a CPU una sola vez
        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        confidences = result.boxes.conf.cpu().numpy()

        names = result.names

        for box, class_id, confidence in zip(
            boxes,
            classes,
            confidences,
        ):
            class_name = names[class_id]

            detections.setdefault(class_name, []).append(
                {
                    "box": box.tolist(),
                    "confidence": float(confidence),
                }
            )

        return detections