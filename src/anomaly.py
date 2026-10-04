class AnomalyEngine:
    """
    Evaluates observable movement characteristics and produces
    a situational-awareness score.

    This engine does not identify people or infer intent.
    It evaluates only measurable motion and spatial features.
    """

    def __init__(
        self,
        suspicious_threshold=40,
        alert_threshold=70
    ):
        if not 0 <= suspicious_threshold <= 100:
            raise ValueError(
                "suspicious_threshold must be between 0 and 100"
            )

        if not 0 <= alert_threshold <= 100:
            raise ValueError(
                "alert_threshold must be between 0 and 100"
            )

        if suspicious_threshold >= alert_threshold:
            raise ValueError(
                "suspicious_threshold must be lower than "
                "alert_threshold"
            )

        self.suspicious_threshold = suspicious_threshold
        self.alert_threshold = alert_threshold

    def evaluate(
        self,
        behavior=None,
        motion=None,
        zone_type=None,
        dwell_seconds=0.0
    ):
        score = 0
        reasons = []

        # --------------------------------------------------
        # BEHAVIOR
        # --------------------------------------------------

        if behavior:
            if behavior.get("status") == "ANOMALY":
                score += 30

                reason = behavior.get("reason")

                if reason:
                    reasons.append(reason)

        # --------------------------------------------------
        # ZONE
        # --------------------------------------------------

        if zone_type == "RESTRICTED":
            score += 25
            reasons.append("RESTRICTED_ZONE")

        elif zone_type == "HIGH_SENSITIVITY":
            score += 35
            reasons.append("HIGH_SENSITIVITY_ZONE")

        # --------------------------------------------------
        # DWELL TIME
        # --------------------------------------------------

        if dwell_seconds >= 30:
            score += 15
            reasons.append("LONG_DWELL")

        # --------------------------------------------------
        # MOTION
        # --------------------------------------------------

        if motion:
            speed = motion.get("speed")

            if speed is not None and speed >= 250:
                score += 20
                reasons.append("HIGH_SPEED")

        # --------------------------------------------------
        # LIMIT SCORE
        # --------------------------------------------------

        score = min(score, 100)

        # --------------------------------------------------
        # CLASSIFY
        # --------------------------------------------------

        if score >= self.alert_threshold:
            status = "ALERT"

        elif score >= self.suspicious_threshold:
            status = "SUSPICIOUS"

        else:
            status = "NORMAL"

        return {
            "score": score,
            "status": status,
            "reasons": reasons
        }