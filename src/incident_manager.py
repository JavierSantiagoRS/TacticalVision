from datetime import datetime, timezone


class IncidentManager:
    """
    Manages the lifecycle of analytical incidents.

    An incident is an aggregation of observable computer-vision
    events and alerts associated with the same tracked object
    and zone.

    This module does not determine real-world intent or threat.
    """

    ACTIVE_STATES = {
        "DETECTED",
        "ASSESSING",
        "ACTIVE",
    }

    RESOLVED_STATE = "RESOLVED"

    def __init__(self):
        self.incidents = {}
        self.next_id = 1

    # ==================================================
    # CREATE INCIDENT
    # ==================================================

    def create(
        self,
        object_id,
        object_class,
        zone,
        priority="LOW",
        reasons=None,
    ):
        if reasons is None:
            reasons = []

        incident_id = self.next_id

        self.next_id += 1

        incident = {
            "id": incident_id,
            "object_id": object_id,
            "object_class": object_class,
            "zone": zone,
            "priority": priority,
            "status": "DETECTED",
            "reasons": list(reasons),
            "created_at": self._timestamp(),
            "updated_at": self._timestamp(),
        }

        self.incidents[incident_id] = incident

        return dict(incident)

    # ==================================================
    # UPDATE INCIDENT
    # ==================================================

    def update(
        self,
        incident_id,
        priority=None,
        status=None,
        reasons=None,
    ):
        incident = self.incidents.get(
            incident_id
        )

        if incident is None:
            return None

        if priority is not None:
            incident["priority"] = priority

        if status is not None:
            incident["status"] = status

        if reasons is not None:
            incident["reasons"] = list(
                reasons
            )

        incident["updated_at"] = (
            self._timestamp()
        )

        return dict(incident)

    # ==================================================
    # RESOLVE INCIDENT
    # ==================================================

    def resolve(self, incident_id):
        return self.update(
            incident_id,
            status=self.RESOLVED_STATE,
        )

    # ==================================================
    # GET INCIDENT
    # ==================================================

    def get(self, incident_id):
        incident = self.incidents.get(
            incident_id
        )

        if incident is None:
            return None

        return dict(incident)

    # ==================================================
    # ACTIVE INCIDENTS
    # ==================================================

    def active(self):
        return [
            dict(incident)
            for incident in self.incidents.values()
            if incident["status"]
            in self.ACTIVE_STATES
        ]

    # ==================================================
    # ALL INCIDENTS
    # ==================================================

    def all(self):
        return [
            dict(incident)
            for incident in self.incidents.values()
        ]

    # ==================================================
    # REMOVE TRACK
    # ==================================================

    def remove_object(self, object_id):
        """
        Resolve active incidents belonging to a
        track that is no longer active.
        """

        resolved = []

        for incident in self.incidents.values():

            if (
                incident["object_id"]
                == object_id
                and incident["status"]
                in self.ACTIVE_STATES
            ):
                incident["status"] = (
                    self.RESOLVED_STATE
                )

                incident["updated_at"] = (
                    self._timestamp()
                )

                resolved.append(
                    dict(incident)
                )

        return resolved

    # ==================================================
    # TIMESTAMP
    # ==================================================

    @staticmethod
    def _timestamp():
        return datetime.now(
            timezone.utc
        ).isoformat()