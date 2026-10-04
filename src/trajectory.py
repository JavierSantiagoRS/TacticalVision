from collections import defaultdict, deque


class TrajectoryTracker:

    def __init__(
        self,
        max_points=40,
        max_missing_frames=10
    ):
        self.max_points = max_points
        self.max_missing_frames = max_missing_frames

        self.trajectories = defaultdict(
            lambda: deque(
                maxlen=self.max_points
            )
        )

        self.missing_frames = defaultdict(int)

    def update(self, object_id, x, y):

        self.trajectories[object_id].append(
            (x, y)
        )

        self.missing_frames[object_id] = 0

    def get(self, object_id):

        return list(
            self.trajectories[object_id]
        )

    def remove(self, active_ids):

        tracked_ids = list(
            self.trajectories.keys()
        )

        for object_id in tracked_ids:

            if object_id in active_ids:

                self.missing_frames[
                    object_id
                ] = 0

                continue

            self.missing_frames[
                object_id
            ] += 1

            if (
                self.missing_frames[object_id]
                > self.max_missing_frames
            ):

                del self.trajectories[
                    object_id
                ]

                del self.missing_frames[
                    object_id
                ]