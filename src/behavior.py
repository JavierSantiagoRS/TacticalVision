import math
from collections import defaultdict, deque


class BehaviorAnalyzer:
    """
    Analyzes tracked-object trajectories and detects
    geometric movement anomalies.

    This module does not identify people or determine intent.
    It only evaluates movement characteristics from tracked
    object coordinates.
    """

    def __init__(
        self,
        history_size=20,
        direction_change_threshold=4,
        minimum_movement=8.0,
        minimum_history=6,
        anomaly_persistence=2
    ):
        self.history_size = history_size

        self.direction_change_threshold = (
            direction_change_threshold
        )

        self.minimum_movement = (
            minimum_movement
        )

        self.minimum_history = (
            minimum_history
        )

        self.anomaly_persistence = (
            anomaly_persistence
        )

        self.history = defaultdict(
            lambda: deque(
                maxlen=self.history_size
            )
        )

        self.anomaly_counters = defaultdict(int)

    def update(
        self,
        object_id,
        x,
        y
    ):
        history = self.history[object_id]

        history.append(
            (x, y)
        )

        if len(history) < self.minimum_history:

            self.anomaly_counters[
                object_id
            ] = 0

            return {
                "status": "NORMAL",
                "reason": None,
                "direction_changes": 0
            }

        direction_changes = (
            self._count_direction_changes(
                history
            )
        )

        if (
            direction_changes
            >= self.direction_change_threshold
        ):

            self.anomaly_counters[
                object_id
            ] += 1

        else:

            self.anomaly_counters[
                object_id
            ] = 0

        if (
            self.anomaly_counters[object_id]
            >= self.anomaly_persistence
        ):

            return {
                "status": "ANOMALY",
                "reason": "FREQUENT_DIRECTION_CHANGES",
                "direction_changes": direction_changes
            }

        return {
            "status": "NORMAL",
            "reason": None,
            "direction_changes": direction_changes
        }

    def _count_direction_changes(
        self,
        history
    ):
        changes = 0
        previous_direction = None

        for index in range(
            1,
            len(history)
        ):

            x1, y1 = history[
                index - 1
            ]

            x2, y2 = history[
                index
            ]

            dx = x2 - x1
            dy = y2 - y1

            distance = math.hypot(
                dx,
                dy
            )

            if (
                distance
                < self.minimum_movement
            ):
                continue

            direction = self._direction(
                dx,
                dy
            )

            if (
                previous_direction
                is not None
                and direction
                != previous_direction
            ):

                changes += 1

            previous_direction = direction

        return changes

    def _direction(
        self,
        dx,
        dy
    ):
        if abs(dx) > abs(dy):

            if dx > 0:
                return "EAST"

            return "WEST"

        if dy > 0:
            return "SOUTH"

        return "NORTH"

    def remove(
        self,
        active_ids
    ):
        inactive_ids = [
            object_id
            for object_id in self.history
            if object_id not in active_ids
        ]

        for object_id in inactive_ids:

            del self.history[
                object_id
            ]

            self.anomaly_counters.pop(
                object_id,
                None
            )