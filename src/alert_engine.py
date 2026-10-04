class AlertEngine:
    """
    Manages alert state transitions for tracked objects.

    Threat priority and alert state are intentionally kept
    separate.

    Threat priority:
        NORMAL
        LOW
        MEDIUM
        HIGH

    Alert state:
        NORMAL
        SUSPICIOUS
        ALERT

    This module does not determine intent or real-world threat.
    It only manages transitions produced by the analytical
    pipeline.
    """

    ALERT_STATES = {
        "NORMAL",
        "SUSPICIOUS",
        "ALERT",
    }

    def __init__(self):
        self.states = {}

    def update(
        self,
        object_id,
        zone,
        status,
        score,
        reasons=None
    ):
        if reasons is None:
            reasons = []

        if status not in self.ALERT_STATES:
            raise ValueError(
                f"Invalid alert status: {status}"
            )

        key = (
            object_id,
            zone
        )

        previous_status = self.states.get(
            key,
            "NORMAL"
        )

        alert = None

        # ----------------------------------------------
        # NEW ALERT
        # ----------------------------------------------

        if (
            status in {
                "SUSPICIOUS",
                "ALERT"
            }
            and previous_status == "NORMAL"
        ):

            alert = {
                "type": "ALERT",
                "object_id": object_id,
                "zone": zone,
                "status": status,
                "score": score,
                "reasons": list(reasons)
            }

        # ----------------------------------------------
        # STATE UPDATE
        # ----------------------------------------------

        self.states[key] = status

        return alert

    def get_state(
        self,
        object_id,
        zone
    ):
        """
        Return the current alert state.
        """

        return self.states.get(
            (
                object_id,
                zone
            ),
            "NORMAL"
        )

    def remove(self, active_ids):
        """
        Remove state belonging to tracks that are
        no longer active.
        """

        stale_keys = [
            key
            for key in self.states
            if key[0] not in active_ids
        ]

        for key in stale_keys:

            del self.states[key]