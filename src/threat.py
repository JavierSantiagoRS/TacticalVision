class ThreatAssessment:
    """
    Educational risk-priority assessment engine.

    This module evaluates observable computer-vision signals only.

    It does NOT:
    - identify people,
    - determine intent,
    - classify individuals as threats,
    - perform targeting,
    - make real-world threat determinations.

    The resulting priority is an analytical classification
    based exclusively on configured visual signals.
    """

    LEVELS = {
        "NORMAL": 0,
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
    }

    def __init__(
        self,
        medium_speed=120.0,
        high_speed=250.0,
    ):
        if medium_speed < 0:
            raise ValueError(
                "medium_speed must be >= 0"
            )

        if high_speed <= medium_speed:
            raise ValueError(
                "high_speed must be greater than medium_speed"
            )

        self.medium_speed = float(
            medium_speed
        )

        self.high_speed = float(
            high_speed
        )

    # ==================================================
    # PUBLIC API
    # ==================================================

    def assess(
        self,
        object_class,
        zone_name,
        speed=0.0,
        behavior_status="NORMAL",
    ):
        """
        Calculate an analytical priority level.

        Parameters:
            object_class:
                Detected object category.

            zone_name:
                Current spatial zone.

            speed:
                Approximate pixel speed.

            behavior_status:
                Observable behavior state.

        Returns:
            dict:
                {
                    "priority": str,
                    "score": int,
                    "reasons": list[str]
                }
        """

        speed = self._normalize_speed(
            speed
        )

        behavior_status = (
            behavior_status.upper()
            if isinstance(
                behavior_status,
                str
            )
            else "NORMAL"
        )

        score = 0
        reasons = []

        # ----------------------------------------------
        # OBSERVABLE SIGNALS
        # ----------------------------------------------

        score += self._evaluate_speed(
            speed,
            reasons
        )

        score += self._evaluate_behavior(
            behavior_status,
            reasons
        )

        score += self._evaluate_zone(
            zone_name,
            reasons
        )

        score += self._evaluate_object_class(
            object_class,
            reasons
        )

        # ----------------------------------------------
        # PRIORITY
        # ----------------------------------------------

        priority = self._calculate_priority(
            score,
            reasons
        )

        return {
            "priority": priority,
            "score": score,
            "reasons": reasons,
        }

    # ==================================================
    # SPEED
    # ==================================================

    def _evaluate_speed(
        self,
        speed,
        reasons
    ):
        """
        Evaluate observable object movement speed.

        Returns:
            Score contribution.
        """

        if speed >= self.high_speed:

            reasons.append(
                "HIGH_SPEED"
            )

            return 2

        if speed >= self.medium_speed:

            reasons.append(
                "ELEVATED_SPEED"
            )

            return 1

        return 0

    # ==================================================
    # BEHAVIOR
    # ==================================================

    def _evaluate_behavior(
        self,
        behavior_status,
        reasons
    ):
        """
        Evaluate previously computed observable behavior.

        Returns:
            Score contribution.
        """

        if behavior_status == "ANOMALY":

            reasons.append(
                "ANOMALOUS_TRAJECTORY"
            )

            return 2

        return 0

    # ==================================================
    # ZONE
    # ==================================================

    def _evaluate_zone(
        self,
        zone_name,
        reasons
    ):
        """
        Evaluate whether the object is currently
        associated with a configured spatial zone.
        """

        if (
            zone_name
            and zone_name != "NO_ZONE"
        ):

            reasons.append(
                "ZONE_ACTIVITY"
            )

            return 1

        return 0

    # ==================================================
    # OBJECT CLASS
    # ==================================================

    def _evaluate_object_class(
        self,
        object_class,
        reasons
    ):
        """
        Add a small analytical weight to relevant
        object categories.

        This is an object-class signal only and does
        not imply intent or identity.
        """

        if object_class in {
            "person",
            "vehicle",
        }:

            reasons.append(
                "RELEVANT_OBJECT_CLASS"
            )

            return 1

        return 0

    # ==================================================
    # PRIORITY
    # ==================================================

    def _calculate_priority(
        self,
        score,
        reasons
    ):
        """
        Convert the accumulated analytical score
        into a priority level.
        """

        strong_signal = (
            "ANOMALOUS_TRAJECTORY"
            in reasons
            or
            "HIGH_SPEED"
            in reasons
        )

        # ----------------------------------------------
        # HIGH
        # ----------------------------------------------

        if (
            strong_signal
            and score >= 5
        ):
            return "HIGH"

        # ----------------------------------------------
        # MEDIUM
        # ----------------------------------------------

        if strong_signal:
            return "MEDIUM"

        if score >= 3:
            return "MEDIUM"

        # ----------------------------------------------
        # LOW
        # ----------------------------------------------

        if score >= 1:
            return "LOW"

        # ----------------------------------------------
        # NORMAL
        # ----------------------------------------------

        return "NORMAL"

    # ==================================================
    # VALIDATION
    # ==================================================

    @staticmethod
    def _normalize_speed(
        speed
    ):
        """
        Normalize speed into a non-negative float.
        """

        try:

            speed = float(
                speed
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0

        return max(
            speed,
            0.0
        )
