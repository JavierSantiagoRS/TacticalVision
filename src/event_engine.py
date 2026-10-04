class EventEngine:
    """
    Detects ENTER and EXIT transitions for tracked objects.

    A state transition must remain stable for a configurable
    number of consecutive frames before an event is emitted.

    Example:

        confirmation_frames=1
            -> transition is emitted immediately.

        confirmation_frames=3
            -> transition must be observed for 3 consecutive
               frames before an event is emitted.
    """

    def __init__(self, confirmation_frames=3):
        if confirmation_frames < 1:
            raise ValueError(
                "confirmation_frames must be >= 1"
            )

        self.confirmation_frames = confirmation_frames

        # Last confirmed state.
        #
        # Key:
        #     (object_id, zone_name)
        #
        # Value:
        #     True  -> object is confirmed inside
        #     False -> object is confirmed outside
        self.previous_states = {}

        # Candidate state currently being confirmed.
        self.pending_states = {}

        # Number of consecutive frames supporting
        # the pending state.
        self.pending_counts = {}

    def update(
        self,
        object_id,
        object_class,
        x,
        y,
        zone,
        confidence=None,
        direction=None,
        speed=None
    ):
        """
        Process one observation of an object relative to a zone.

        Returns:
            dict | None:
                ENTER or EXIT event when a transition
                has been confirmed.
        """

        currently_inside = zone.contains(
            x,
            y
        )

        key = (
            object_id,
            zone.name
        )

        # --------------------------------------------------
        # INITIALIZE STATE
        # --------------------------------------------------
        #
        # An object that appears for the first time should
        # establish its current state without generating
        # an artificial EXIT event.
        #
        # If it appears inside the zone, however, that is
        # considered an ENTER transition.
        #
        # To preserve the existing application semantics,
        # the initial state is considered OUTSIDE.
        #
        if key not in self.previous_states:

            self.previous_states[key] = False

        previous_inside = self.previous_states[key]

        # --------------------------------------------------
        # NO TRANSITION
        # --------------------------------------------------

        if currently_inside == previous_inside:

            # Current observation agrees with the confirmed
            # state, therefore any previous candidate is no
            # longer valid.
            self.pending_states.pop(
                key,
                None
            )

            self.pending_counts.pop(
                key,
                None
            )

            return None

        # --------------------------------------------------
        # TRANSITION CANDIDATE
        # --------------------------------------------------

        pending_state = self.pending_states.get(
            key
        )

        # A new candidate transition has started.
        if pending_state != currently_inside:

            self.pending_states[key] = (
                currently_inside
            )

            self.pending_counts[key] = 1

        else:
            # Same candidate has remained stable.
            self.pending_counts[key] += 1

        # --------------------------------------------------
        # CHECK CONFIRMATION
        # --------------------------------------------------

        if (
            self.pending_counts[key]
            < self.confirmation_frames
        ):
            return None

        # --------------------------------------------------
        # CONFIRMED EVENT
        # --------------------------------------------------

        event_type = (
            "ENTER"
            if currently_inside
            else "EXIT"
        )

        event = {
            "type": event_type,
            "object_id": object_id,
            "object_class": object_class,
            "zone": zone.name,
            "confidence": confidence,
            "direction": direction,
            "speed": speed
        }

        # --------------------------------------------------
        # COMMIT STATE
        # --------------------------------------------------

        self.previous_states[key] = (
            currently_inside
        )

        self.pending_states.pop(
            key,
            None
        )

        self.pending_counts.pop(
            key,
            None
        )

        return event

    def remove(self, active_ids):
        """
        Remove state belonging to objects that are no
        longer actively tracked.

        Args:
            active_ids:
                Set containing currently active object IDs.
        """

        # Collect keys from ALL state dictionaries.
        #
        # This is important because an object may exist only
        # in pending_states/pending_counts and not yet have
        # a confirmed transition.
        all_keys = set(
            self.previous_states.keys()
        )

        all_keys.update(
            self.pending_states.keys()
        )

        all_keys.update(
            self.pending_counts.keys()
        )

        stale_keys = [
            key
            for key in all_keys
            if key[0] not in active_ids
        ]

        for key in stale_keys:

            self.previous_states.pop(
                key,
                None
            )

            self.pending_states.pop(
                key,
                None
            )

            self.pending_counts.pop(
                key,
                None
            )