from collections import Counter, deque


class ClassStabilizer:
    """
    Stabilizes object-class predictions across frames.

    A tracked object may receive inconsistent class predictions
    from the detector. This component maintains a short history
    for each track and returns the most frequently observed class.

    This is a temporal smoothing mechanism. It does not perform
    identity recognition or infer intent.
    """

    def __init__(
        self,
        history_size=8,
        minimum_observations=3
    ):
        if history_size <= 0:
            raise ValueError(
                "history_size must be greater than 0"
            )

        if minimum_observations <= 0:
            raise ValueError(
                "minimum_observations must be greater than 0"
            )

        if minimum_observations > history_size:
            raise ValueError(
                "minimum_observations cannot exceed history_size"
            )

        self.history_size = int(
            history_size
        )

        self.minimum_observations = int(
            minimum_observations
        )

        self.histories = {}

    def update(
        self,
        object_id,
        object_class
    ):
        """
        Add a class observation and return the stabilized class.
        """

        if object_id not in self.histories:
            self.histories[object_id] = deque(
                maxlen=self.history_size
            )

        history = self.histories[object_id]

        history.append(
            object_class
        )

        counts = Counter(
            history
        )

        most_common_class, count = (
            counts.most_common(1)[0]
        )

        if len(history) < self.minimum_observations:
            return object_class

        return most_common_class

    def get(
        self,
        object_id
    ):
        """
        Return the currently stabilized class.

        Returns None if the object has no history.
        """

        history = self.histories.get(
            object_id
        )

        if not history:
            return None

        counts = Counter(
            history
        )

        return counts.most_common(1)[0][0]

    def remove(
        self,
        active_ids
    ):
        """
        Remove histories belonging to inactive tracks.
        """

        stale_ids = [
            object_id
            for object_id in self.histories
            if object_id not in active_ids
        ]

        for object_id in stale_ids:
            del self.histories[
                object_id
            ]

    def clear(self):
        """
        Remove all stored class histories.
        """

        self.histories.clear()