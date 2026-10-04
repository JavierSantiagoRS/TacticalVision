import pytest

from src.anomaly import AnomalyEngine


def test_normal_behavior():
    engine = AnomalyEngine()

    result = engine.evaluate()

    assert result["score"] == 0
    assert result["status"] == "NORMAL"
    assert result["reasons"] == []


def test_behavior_anomaly():
    engine = AnomalyEngine()

    result = engine.evaluate(
        behavior={
            "status": "ANOMALY",
            "reason": "FREQUENT_DIRECTION_CHANGES"
        }
    )

    assert result["score"] == 30
    assert result["status"] == "NORMAL"
    assert "FREQUENT_DIRECTION_CHANGES" in result["reasons"]


def test_restricted_zone():
    engine = AnomalyEngine()

    result = engine.evaluate(
        zone_type="RESTRICTED"
    )

    assert result["score"] == 25
    assert result["status"] == "NORMAL"
    assert "RESTRICTED_ZONE" in result["reasons"]


def test_suspicious_status():
    engine = AnomalyEngine()

    result = engine.evaluate(
        behavior={
            "status": "ANOMALY",
            "reason": "FREQUENT_DIRECTION_CHANGES"
        },
        zone_type="RESTRICTED"
    )

    assert result["score"] == 55
    assert result["status"] == "SUSPICIOUS"


def test_alert_status():
    engine = AnomalyEngine()

    result = engine.evaluate(
        behavior={
            "status": "ANOMALY",
            "reason": "FREQUENT_DIRECTION_CHANGES"
        },
        zone_type="HIGH_SENSITIVITY",
        dwell_seconds=30
    )

    assert result["score"] == 80
    assert result["status"] == "ALERT"


def test_high_speed():
    engine = AnomalyEngine()

    result = engine.evaluate(
        motion={
            "speed": 300
        }
    )

    assert result["score"] == 20
    assert "HIGH_SPEED" in result["reasons"]


def test_score_is_limited_to_100():
    engine = AnomalyEngine()

    result = engine.evaluate(
        behavior={
            "status": "ANOMALY",
            "reason": "FREQUENT_DIRECTION_CHANGES"
        },
        zone_type="HIGH_SENSITIVITY",
        dwell_seconds=100,
        motion={
            "speed": 500
        }
    )

    assert result["score"] == 100


def test_invalid_thresholds():
    with pytest.raises(ValueError):
        AnomalyEngine(
            suspicious_threshold=80,
            alert_threshold=70
        )


def test_threshold_range():
    with pytest.raises(ValueError):
        AnomalyEngine(
            suspicious_threshold=-1
        )