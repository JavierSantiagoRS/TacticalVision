class TacticalState:
    """
    Centralized operational state for TacticalVision.

    Stores the current state of tracked objects,
    alerts, events and system statistics.

    Educational computer-vision component.
    """

    def __init__(self):
        self.tracks = {}
        self.alerts = []
        self.events = []

        self.statistics = {
            "active_tracks": 0,
            "total_events": 0,
            "total_alerts": 0,
        }

        self.system_status = "INITIALIZING"

    # ==================================================
    # SYSTEM
    # ==================================================

    def set_system_status(self, status):
        self.system_status = status

    # ==================================================
    # TRACKS
    # ==================================================

    def update_track(
        self,
        object_id,
        object_class,
        zone,
        speed=0.0,
        direction="UNKNOWN",
        behavior="NORMAL",
        priority="NORMAL",
    ):
        self.tracks[object_id] = {
            "object_id": object_id,
            "class": object_class,
            "zone": zone,
            "speed": speed,
            "direction": direction,
            "behavior": behavior,
            "priority": priority,
        }

        self.statistics["active_tracks"] = len(
            self.tracks
        )

    def remove_tracks(self, active_ids):
        stale_ids = [
            object_id
            for object_id in self.tracks
            if object_id not in active_ids
        ]

        for object_id in stale_ids:
            del self.tracks[object_id]

        self.statistics["active_tracks"] = len(
            self.tracks
        )

    # ==================================================
    # EVENTS
    # ==================================================

    def add_event(self, event):
        self.events.append(event)

        self.statistics["total_events"] += 1

    # ==================================================
    # ALERTS
    # ==================================================

    def add_alert(self, alert):
        self.alerts.append(alert)

        self.statistics["total_alerts"] += 1

    # ==================================================
    # SNAPSHOT
    # ==================================================

    def snapshot(self):
        return {
            "system_status": self.system_status,
            "tracks": dict(self.tracks),
            "alerts": list(self.alerts),
            "events": list(self.events),
            "statistics": dict(self.statistics),
        }