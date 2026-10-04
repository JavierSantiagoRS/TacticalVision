import cv2

from src.config import CAMERA_SOURCE


class Camera:
    """
    OpenCV camera abstraction.
    """

    def __init__(self, source=CAMERA_SOURCE):
        self.source = source
        self.capture = None

    def open(self):
        self.capture = cv2.VideoCapture(self.source)

        if not self.capture.isOpened():
            raise RuntimeError(
                f"No se pudo abrir la cámara: {self.source}"
            )

    def read(self):
        if self.capture is None:
            raise RuntimeError(
                "La cámara no está inicializada."
            )

        success, frame = self.capture.read()

        if not success:
            raise RuntimeError(
                "No se pudo obtener un frame."
            )

        return frame

    def release(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None