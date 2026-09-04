import cv2

from ultralytics import YOLO
from ultralytics.utils.plotting import colors


class PPEDetector:

    def __init__(self, model_path, confidence=0.25):
        self.model = YOLO(model_path)
        self.confidence = confidence

    def predict(self, frame):
        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            imgsz=1024,
            device=0,
            verbose=False,
        )

        return results[0]

    def draw(self, frame, result, display_names=None):
        annotated = frame.copy()

        if result.boxes is None:
            return annotated

        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        confidences = result.boxes.conf.cpu().numpy()

        for box, class_id, confidence in zip(
            boxes,
            classes,
            confidences,
        ):
            x1, y1, x2, y2 = map(int, box)

            original_name = result.names[class_id]

            if display_names:
                class_name = display_names.get(
                    original_name,
                    original_name,
                )
            else:
                class_name = original_name

            label = f"{class_name} {confidence:.2f}"
            color = colors(class_id, bgr=True)

            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                color,
                2,
            )

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2

            (text_width, text_height), baseline = cv2.getTextSize(
                label,
                font,
                font_scale,
                thickness,
            )

            label_y1 = max(
                0,
                y1 - text_height - baseline - 8,
            )

            cv2.rectangle(
                annotated,
                (x1, label_y1),
                (x1 + text_width + 10, y1),
                color,
                -1,
            )

            cv2.putText(
                annotated,
                label,
                (x1 + 5, y1 - baseline - 4),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA,
            )

        return annotated

    def get_detections(self, result):
        detections = {}

        if result.boxes is None or len(result.boxes) == 0:
            return detections

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

            detections.setdefault(
                class_name,
                [],
            ).append(
                {
                    "box": box.tolist(),
                    "confidence": float(confidence),
                }
            )

        return detections
