class AlertPolicy:
    """
    Converts analytical threat priority into an alert state.

    This is a policy layer, not a threat detector.
    """

    def evaluate(self, priority):
        """
        Convert threat priority into alert state.

        NORMAL / LOW
            -> NORMAL

        MEDIUM
            -> SUSPICIOUS

        HIGH
            -> ALERT
        """

        if priority in {
            "NORMAL",
            "LOW"
        }:
            return "NORMAL"

        if priority == "MEDIUM":
            return "SUSPICIOUS"

        if priority == "HIGH":
            return "ALERT"

        raise ValueError(
            f"Unknown threat priority: {priority}"
        )