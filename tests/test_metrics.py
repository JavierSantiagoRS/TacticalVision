from src.metrics import Metrics


def test_metrics_initial_state():

    metrics = Metrics()

    assert metrics.total_frames == 0
    assert metrics.total_events == 0
    assert metrics.active_objects == 0


def test_event_counter():

    metrics = Metrics()

    metrics.record_event()
    metrics.record_event()

    assert metrics.total_events == 2


def test_active_objects():

    metrics = Metrics()

    metrics.set_active_objects(5)

    assert metrics.active_objects == 5


def test_snapshot():

    metrics = Metrics()

    metrics.set_active_objects(3)
    metrics.record_event()

    snapshot = metrics.snapshot()

    assert snapshot["active_objects"] == 3
    assert snapshot["total_events"] == 1