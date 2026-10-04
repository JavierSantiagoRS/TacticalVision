from ultralytics import YOLO

from src.config import (
    CONFIDENCE_THRESHOLD,
    IMAGE_SIZE,
    MODEL_PATH,
    TRACKER_CONFIG,
)


class ObjectTracker:
    """
    YOLO object detector + ByteTrack object tracker.

    Responsible only for object detection and tracking.
    """

    def __init__(
        self,
        model_path=MODEL_PATH,
        image_size=IMAGE_SIZE,
        confidence=CONFIDENCE_THRESHOLD,
        tracker_config=TRACKER_CONFIG,
    ):
        self.model = YOLO(model_path)

        self.image_size = image_size
        self.confidence = confidence
        self.tracker_config = tracker_config

    def track(self, frame):
        """
        Run YOLO tracking on a frame.

        Args:
            frame: OpenCV BGR image.

        Returns:
            Ultralytics Results object.
        """

        results = self.model.track(
            frame,
            persist=True,
            imgsz=self.image_size,
            conf=self.confidence,
            tracker=self.tracker_config,
            verbose=False,
        )

        if not results:
            return None

        return results[0]