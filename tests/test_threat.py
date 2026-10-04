from src.threat import ThreatAssessment


def test_normal_object():

    analyzer = ThreatAssessment()

    result = analyzer.assess(
        object_class="bird",
        zone_name="NO_ZONE",
        speed=0,
        behavior_status="NORMAL",
    )

    assert result["priority"] == "NORMAL"
    assert result["score"] == 0
    assert result["reasons"] == []


def test_zone_activity_creates_low_priority():

    analyzer = ThreatAssessment()

    result = analyzer.assess(
        object_class="bird",
        zone_name="ZONE_1",
        speed=0,
        behavior_status="NORMAL",
    )

    assert result["priority"] == "LOW"
    assert result["score"] == 1
    assert "ZONE_ACTIVITY" in result["reasons"]


def test_elevated_speed():

    analyzer = ThreatAssessment()

    result = analyzer.assess(
        object_class="bird",
        zone_name="NO_ZONE",
        speed=150,
        behavior_status="NORMAL",
    )

    assert result["priority"] == "LOW"
    assert "ELEVATED_SPEED" in result["reasons"]


def test_anomalous_behavior():

    analyzer = ThreatAssessment()

    result = analyzer.assess(
        object_class="bird",
        zone_name="NO_ZONE",
        speed=0,
        behavior_status="ANOMALY",
    )

    assert result["priority"] == "MEDIUM"
    assert "ANOMALOUS_TRAJECTORY" in result["reasons"]


def test_high_speed():

    analyzer = ThreatAssessment()

    result = analyzer.assess(
        object_class="bird",
        zone_name="NO_ZONE",
        speed=300,
        behavior_status="NORMAL",
    )

    assert result["priority"] == "MEDIUM"
    assert "HIGH_SPEED" in result["reasons"]


def test_combined_signals():

    analyzer = ThreatAssessment()

    result = analyzer.assess(
        object_class="person",
        zone_name="ZONE_1",
        speed=300,
        behavior_status="ANOMALY",
    )

    assert result["priority"] == "HIGH"

    assert result["score"] == 6

    assert "HIGH_SPEED" in result["reasons"]
    assert "ANOMALOUS_TRAJECTORY" in result["reasons"]
    assert "ZONE_ACTIVITY" in result["reasons"]
    assert "RELEVANT_OBJECT_CLASS" in result["reasons"]