from ultralytics import YOLO

from src.config import (
    MODEL_PATH,
    IMAGE_SIZE,
    CONFIDENCE_THRESHOLD
)


class ObjectDetector:

    def __init__(
        self,
        model_path=MODEL_PATH,
        image_size=IMAGE_SIZE,
        confidence=CONFIDENCE_THRESHOLD
    ):

        self.model = YOLO(model_path)

        self.image_size = image_size
        self.confidence = confidence

    def detect(self, frame):

        results = self.model(
            frame,
            imgsz=self.image_size,
            conf=self.confidence,
            verbose=False
        )

        return results[0]