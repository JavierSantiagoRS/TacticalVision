import threading
import time

import cv2


class VideoStream:
    """
    Thread-safe container for the latest processed video frame.

    The vision pipeline publishes frames here and the API
    can read the latest available frame without opening
    another camera connection.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._frame = None

    def update(self, frame):
        """
        Store the latest frame.
        """

        if frame is None:
            return

        with self._lock:
            self._frame = frame.copy()

    def get_frame(self):
        """
        Return a copy of the latest frame.
        """

        with self._lock:

            if self._frame is None:
                return None

            return self._frame.copy()

    def encode_jpeg(self, quality=80):
        """
        Encode the latest frame as JPEG.

        Returns:
            bytes | None
        """

        frame = self.get_frame()

        if frame is None:
            return None

        success, buffer = cv2.imencode(
            ".jpg",
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                quality
            ]
        )

        if not success:
            return None

        return buffer.tobytes()

    def wait_for_frame(self, timeout=5.0):
        """
        Wait until a frame becomes available.
        """

        start = time.perf_counter()

        while time.perf_counter() - start < timeout:

            if self.get_frame() is not None:
                return True

            time.sleep(0.01)

        return False