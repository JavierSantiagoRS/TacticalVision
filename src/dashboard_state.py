from threading import Lock


class DashboardState:
    """
    Shared runtime state between TacticalVision
    and the FastAPI dashboard.
    """

    def __init__(self):
        self._lock = Lock()

        self.metrics = {
            "fps": 0.0,
            "inference_ms": 0.0,
            "cpu_percent": 0.0,
            "memory_mb": 0.0,
            "active_objects": 0,
            "total_events": 0,
            "total_frames": 0,
        }

        self.status = "OFFLINE"

    def update_metrics(self, metrics):
        if not isinstance(metrics, dict):
            return

        with self._lock:
            self.metrics.update(metrics)

    def set_status(self, status):
        with self._lock:
            self.status = str(status).upper()

    def snapshot(self):
        with self._lock:
            return {
                "status": self.status,
                **self.metrics,
            }


dashboard_state = DashboardState()