import os
import time
from collections import deque

import psutil


class Metrics:

    def __init__(self, window_size=30):
        self.process = psutil.Process(os.getpid())

        self.frame_times = deque(
            maxlen=window_size
        )

        self.inference_times = deque(
            maxlen=window_size
        )

        self.last_frame_time = None

        self.total_frames = 0
        self.total_events = 0

        self.active_objects = 0

    def start_frame(self):
        self.last_frame_time = time.perf_counter()

    def end_frame(self):
        if self.last_frame_time is None:
            return

        elapsed = (
            time.perf_counter()
            - self.last_frame_time
        )

        self.frame_times.append(elapsed)

        self.total_frames += 1

    def record_inference(self, elapsed):
        self.inference_times.append(
            elapsed
        )

    def record_event(self):
        self.total_events += 1

    def set_active_objects(self, count):
        self.active_objects = count

    def get_fps(self):

        if not self.frame_times:
            return 0.0

        average_time = (
            sum(self.frame_times)
            / len(self.frame_times)
        )

        if average_time <= 0:
            return 0.0

        return 1.0 / average_time

    def get_inference_ms(self):

        if not self.inference_times:
            return 0.0

        average_time = (
            sum(self.inference_times)
            / len(self.inference_times)
        )

        return average_time * 1000

    def get_cpu_percent(self):
        return self.process.cpu_percent(
            interval=None
        )

    def get_memory_mb(self):

        memory = self.process.memory_info()

        return memory.rss / (
            1024 * 1024
        )

    def snapshot(self):

        return {
            "fps": self.get_fps(),
            "inference_ms": self.get_inference_ms(),
            "cpu_percent": self.get_cpu_percent(),
            "memory_mb": self.get_memory_mb(),
            "active_objects": self.active_objects,
            "total_events": self.total_events,
            "total_frames": self.total_frames
        }