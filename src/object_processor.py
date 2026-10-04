class ObjectProcessor:
    """
    Coordinates trajectory, motion and behavior analysis
    for tracked objects.

    This component does not render frames or persist events.
    """

    def __init__(
        self,
        trajectory_tracker,
        motion_analyzer,
        behavior_analyzer
    ):
        self.trajectory_tracker = trajectory_tracker
        self.motion_analyzer = motion_analyzer
        self.behavior_analyzer = behavior_analyzer

    def process(
        self,
        object_id,
        x,
        y
    ):
        """
        Process one tracked object.

        Returns:
            dict containing trajectory, motion and behavior data.
        """

        self.trajectory_tracker.update(
            object_id,
            x,
            y
        )

        motion = self.motion_analyzer.update(
            object_id,
            x,
            y
        )

        behavior = self.behavior_analyzer.update(
            object_id,
            x,
            y
        )

        return {
            "motion": motion,
            "behavior": behavior
        }

    def get_trajectory(
        self,
        object_id
    ):
        """
        Return the trajectory of a tracked object.
        """

        return self.trajectory_tracker.get(
            object_id
        )

    def remove_stale(
        self,
        active_ids
    ):
        """
        Remove state belonging to inactive objects.

        All stateful analytical components must remove
        objects that are no longer actively tracked.
        """

        # ----------------------------------------------
        # TRAJECTORY STATE
        # ----------------------------------------------

        self.trajectory_tracker.remove(
            active_ids
        )

        # ----------------------------------------------
        # MOTION STATE
        # ----------------------------------------------

        self.motion_analyzer.remove(
            active_ids
        )

        # ----------------------------------------------
        # BEHAVIOR STATE
        # ----------------------------------------------

        self.behavior_analyzer.remove(
            active_ids
        )
