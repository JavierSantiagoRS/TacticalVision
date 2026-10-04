from src.incident_manager import IncidentManager


def test_create_incident():

    manager = IncidentManager()

    incident = manager.create(
        object_id=10,
        object_class="person",
        zone="ZONE_1",
        priority="MEDIUM",
        reasons=[
            "ZONE_ACTIVITY"
        ],
    )

    assert incident["id"] == 1
    assert incident["object_id"] == 10
    assert incident["object_class"] == "person"
    assert incident["zone"] == "ZONE_1"
    assert incident["priority"] == "MEDIUM"
    assert incident["status"] == "DETECTED"


def test_incident_ids_are_unique():

    manager = IncidentManager()

    first = manager.create(
        1,
        "person",
        "ZONE_1"
    )

    second = manager.create(
        2,
        "vehicle",
        "ZONE_2"
    )

    assert first["id"] != second["id"]
    assert first["id"] == 1
    assert second["id"] == 2


def test_update_incident():

    manager = IncidentManager()

    incident = manager.create(
        1,
        "person",
        "ZONE_1"
    )

    updated = manager.update(
        incident["id"],
        priority="HIGH",
        status="ACTIVE",
        reasons=[
            "HIGH_SPEED",
            "ZONE_ACTIVITY"
        ],
    )

    assert updated["priority"] == "HIGH"
    assert updated["status"] == "ACTIVE"
    assert updated["reasons"] == [
        "HIGH_SPEED",
        "ZONE_ACTIVITY"
    ]


def test_resolve_incident():

    manager = IncidentManager()

    incident = manager.create(
        1,
        "person",
        "ZONE_1"
    )

    resolved = manager.resolve(
        incident["id"]
    )

    assert resolved["status"] == "RESOLVED"


def test_active_returns_only_active_incidents():

    manager = IncidentManager()

    first = manager.create(
        1,
        "person",
        "ZONE_1"
    )

    second = manager.create(
        2,
        "vehicle",
        "ZONE_2"
    )

    manager.resolve(
        first["id"]
    )

    active = manager.active()

    assert len(active) == 1
    assert active[0]["id"] == second["id"]


def test_get_unknown_incident():

    manager = IncidentManager()

    assert manager.get(999) is None


def test_all_returns_all_incidents():

    manager = IncidentManager()

    first = manager.create(
        1,
        "person",
        "ZONE_1"
    )

    second = manager.create(
        2,
        "vehicle",
        "ZONE_2"
    )

    manager.resolve(
        first["id"]
    )

    incidents = manager.all()

    assert len(incidents) == 2


def test_remove_object_resolves_active_incidents():

    manager = IncidentManager()

    incident = manager.create(
        1,
        "person",
        "ZONE_1"
    )

    resolved = manager.remove_object(1)

    assert len(resolved) == 1

    assert (
        resolved[0]["id"]
        == incident["id"]
    )

    assert (
        resolved[0]["status"]
        == "RESOLVED"
    )


def test_remove_object_does_not_affect_other_objects():

    manager = IncidentManager()

    first = manager.create(
        1,
        "person",
        "ZONE_1"
    )

    second = manager.create(
        2,
        "vehicle",
        "ZONE_2"
    )

    manager.remove_object(1)

    assert (
        manager.get(first["id"])["status"]
        == "RESOLVED"
    )

    assert (
        manager.get(second["id"])["status"]
        == "DETECTED"
    )


def test_incident_contains_timestamps():

    manager = IncidentManager()

    incident = manager.create(
        1,
        "person",
        "ZONE_1"
    )

    assert incident["created_at"]
    assert incident["updated_at"]