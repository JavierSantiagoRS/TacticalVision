from src.alert_engine import AlertEngine


def test_normal_state_generates_no_alert():
    engine = AlertEngine()

    alert = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="NORMAL",
        score=10
    )

    assert alert is None


def test_suspicious_state_generates_alert():
    engine = AlertEngine()

    alert = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="SUSPICIOUS",
        score=50,
        reasons=["RESTRICTED_ZONE"]
    )

    assert alert is not None
    assert alert["type"] == "ALERT"
    assert alert["object_id"] == 1
    assert alert["zone"] == "ZONE_1"
    assert alert["status"] == "SUSPICIOUS"
    assert alert["score"] == 50


def test_alert_state_generates_alert():
    engine = AlertEngine()

    alert = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="ALERT",
        score=80,
        reasons=["HIGH_SPEED"]
    )

    assert alert is not None
    assert alert["status"] == "ALERT"
    assert alert["score"] == 80


def test_repeated_alert_does_not_duplicate():
    engine = AlertEngine()

    first = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="ALERT",
        score=80
    )

    second = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="ALERT",
        score=85
    )

    assert first is not None
    assert second is None


def test_alert_can_recover_to_normal():
    engine = AlertEngine()

    first = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="ALERT",
        score=80
    )

    second = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="NORMAL",
        score=10
    )

    third = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="ALERT",
        score=90
    )

    assert first is not None
    assert second is None
    assert third is not None


def test_suspicious_to_alert_does_not_duplicate():
    engine = AlertEngine()

    first = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="SUSPICIOUS",
        score=50
    )

    second = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="ALERT",
        score=80
    )

    assert first is not None
    assert second is None


def test_objects_have_independent_alert_states():
    engine = AlertEngine()

    alert_1 = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="ALERT",
        score=80
    )

    alert_2 = engine.update(
        object_id=2,
        zone="ZONE_1",
        status="ALERT",
        score=90
    )

    assert alert_1 is not None
    assert alert_2 is not None


def test_zones_have_independent_alert_states():
    engine = AlertEngine()

    alert_1 = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="ALERT",
        score=80
    )

    alert_2 = engine.update(
        object_id=1,
        zone="ZONE_2",
        status="ALERT",
        score=80
    )

    assert alert_1 is not None
    assert alert_2 is not None


def test_remove_clears_track_state():
    engine = AlertEngine()

    engine.update(
        object_id=1,
        zone="ZONE_1",
        status="ALERT",
        score=80
    )

    engine.remove(set())

    assert (
        1,
        "ZONE_1"
    ) not in engine.states


def test_reasons_are_preserved():
    engine = AlertEngine()

    alert = engine.update(
        object_id=1,
        zone="ZONE_1",
        status="ALERT",
        score=90,
        reasons=[
            "HIGH_SPEED",
            "LONG_DWELL"
        ]
    )

    assert alert["reasons"] == [
        "HIGH_SPEED",
        "LONG_DWELL"
    ]