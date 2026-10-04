from src.tactical_state import TacticalState


def test_initial_state():

    state = TacticalState()

    snapshot = state.snapshot()

    assert snapshot["system_status"] == "INITIALIZING"
    assert snapshot["tracks"] == {}
    assert snapshot["alerts"] == []
    assert snapshot["events"] == []


def test_system_status():

    state = TacticalState()

    state.set_system_status("OPERATIONAL")

    assert state.system_status == "OPERATIONAL"


def test_track_update():

    state = TacticalState()

    state.update_track(
        object_id=10,
        object_class="person",
        zone="ZONE_1",
        speed=120.5,
        direction="RIGHT",
        behavior="NORMAL",
        priority="LOW",
    )

    track = state.tracks[10]

    assert track["object_id"] == 10
    assert track["class"] == "person"
    assert track["zone"] == "ZONE_1"
    assert track["speed"] == 120.5
    assert track["direction"] == "RIGHT"
    assert track["behavior"] == "NORMAL"
    assert track["priority"] == "LOW"


def test_active_track_count():

    state = TacticalState()

    state.update_track(
        1,
        "person",
        "ZONE_1"
    )

    state.update_track(
        2,
        "vehicle",
        "ZONE_2"
    )

    assert (
        state.statistics["active_tracks"]
        == 2
    )


def test_remove_stale_tracks():

    state = TacticalState()

    state.update_track(
        1,
        "person",
        "ZONE_1"
    )

    state.update_track(
        2,
        "vehicle",
        "ZONE_2"
    )

    state.remove_tracks({2})

    assert 1 not in state.tracks
    assert 2 in state.tracks

    assert (
        state.statistics["active_tracks"]
        == 1
    )


def test_event():

    state = TacticalState()

    event = {
        "type": "ENTER",
        "object_id": 1,
        "zone": "ZONE_1",
    }

    state.add_event(event)

    assert len(state.events) == 1
    assert state.statistics["total_events"] == 1


def test_alert():

    state = TacticalState()

    alert = {
        "type": "ALERT",
        "object_id": 1,
        "zone": "ZONE_1",
        "status": "SUSPICIOUS",
        "score": 50,
    }

    state.add_alert(alert)

    assert len(state.alerts) == 1
    assert state.statistics["total_alerts"] == 1


def test_snapshot_is_available():

    state = TacticalState()

    state.set_system_status(
        "OPERATIONAL"
    )

    state.update_track(
        1,
        "person",
        "ZONE_1",
        priority="MEDIUM"
    )

    snapshot = state.snapshot()

    assert (
        snapshot["system_status"]
        == "OPERATIONAL"
    )

    assert (
        snapshot["statistics"]["active_tracks"]
        == 1
    )

    assert (
        snapshot["tracks"][1]["priority"]
        == "MEDIUM"
    )
def test_track_update_reflects_current_analytical_state():

    state = TacticalState()

    state.update_track(
        object_id=7,
        object_class="person",
        zone="ZONE_2",
        speed=185.0,
        direction="EAST",
        behavior="ANOMALY",
        priority="MEDIUM",
    )

    snapshot = state.snapshot()

    track = snapshot["tracks"][7]

    assert track["object_id"] == 7
    assert track["class"] == "person"
    assert track["zone"] == "ZONE_2"
    assert track["speed"] == 185.0
    assert track["direction"] == "EAST"
    assert track["behavior"] == "ANOMALY"
    assert track["priority"] == "MEDIUM"