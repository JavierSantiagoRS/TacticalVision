import math
import time


class MotionAnalyzer:

    def __init__(self, movement_threshold=3):
        self.previous_positions = {}
        self.previous_times = {}

        self.movement_threshold = (
            movement_threshold
        )

    def update(self, object_id, x, y):

        current_time = time.perf_counter()

        # ----------------------------------------------
        # FIRST OBSERVATION
        # ----------------------------------------------

        if object_id not in self.previous_positions:

            self.previous_positions[
                object_id
            ] = (x, y)

            self.previous_times[
                object_id
            ] = current_time

            return {
                "direction": "STATIONARY",
                "speed": 0.0,
                "delta_x": 0.0,
                "delta_y": 0.0,
                "distance": 0.0,
                "angle": None,
                "state": "STATIONARY"
            }

        # ----------------------------------------------
        # PREVIOUS STATE
        # ----------------------------------------------

        previous_x, previous_y = (
            self.previous_positions[
                object_id
            ]
        )

        previous_time = (
            self.previous_times[
                object_id
            ]
        )

        # ----------------------------------------------
        # DISPLACEMENT
        # ----------------------------------------------

        delta_x = x - previous_x
        delta_y = y - previous_y

        delta_time = (
            current_time
            - previous_time
        )

        # ----------------------------------------------
        # DISTANCE
        # ----------------------------------------------

        distance = math.hypot(
            delta_x,
            delta_y
        )

        # ----------------------------------------------
        # SPEED
        # ----------------------------------------------

        if delta_time <= 0:

            speed = 0.0

        else:

            speed = (
                distance
                / delta_time
            )

        # ----------------------------------------------
        # DIRECTION
        # ----------------------------------------------

        direction = (
            self._calculate_direction(
                delta_x,
                delta_y
            )
        )

        # ----------------------------------------------
        # MOVEMENT STATE
        # ----------------------------------------------

        if distance < self.movement_threshold:

            state = "STATIONARY"

        else:

            state = "MOVING"

        # ----------------------------------------------
        # ANGLE
        # ----------------------------------------------

        if distance < self.movement_threshold:

            angle = None

        else:

            angle = math.degrees(
                math.atan2(
                    delta_y,
                    delta_x
                )
            )

        # ----------------------------------------------
        # UPDATE HISTORY
        # ----------------------------------------------

        self.previous_positions[
            object_id
        ] = (x, y)

        self.previous_times[
            object_id
        ] = current_time

        # ----------------------------------------------
        # RESULT
        # ----------------------------------------------

        return {
            "direction": direction,
            "speed": speed,
            "delta_x": delta_x,
            "delta_y": delta_y,
            "distance": distance,
            "angle": angle,
            "state": state
        }

    def _calculate_direction(
        self,
        delta_x,
        delta_y
    ):

        threshold = (
            self.movement_threshold
        )

        if (
            abs(delta_x) < threshold
            and abs(delta_y) < threshold
        ):

            return "STATIONARY"

        if abs(delta_x) > abs(delta_y):

            if delta_x > 0:

                return "EAST"

            return "WEST"

        if delta_y > 0:

            return "SOUTH"

        return "NORTH"

    def remove(self, active_ids):

        inactive_ids = [
            object_id
            for object_id
            in self.previous_positions
            if object_id not in active_ids
        ]

        for object_id in inactive_ids:

            del self.previous_positions[
                object_id
            ]

            del self.previous_times[
                object_id
            ]