from src.behavior import BehaviorAnalyzer


def test_initial_state_is_normal():
    analyzer = BehaviorAnalyzer()

    result = analyzer.update(
        object_id=1,
        x=100,
        y=100
    )

    assert result["status"] == "NORMAL"
    assert result["reason"] is None


def test_stationary_object_is_normal():
    analyzer = BehaviorAnalyzer(
        minimum_history=3
    )

    for _ in range(10):

        result = analyzer.update(
            object_id=1,
            x=100,
            y=100
        )

    assert result["status"] == "NORMAL"


def test_consistent_movement_is_normal():
    analyzer = BehaviorAnalyzer(
        minimum_history=3,
        direction_change_threshold=4
    )

    for x in range(100, 180, 10):

        result = analyzer.update(
            object_id=1,
            x=x,
            y=100
        )

    assert result["status"] == "NORMAL"


def test_repeated_direction_changes_become_anomaly():
    analyzer = BehaviorAnalyzer(
        history_size=20,
        direction_change_threshold=2,
        minimum_movement=1,
        minimum_history=3,
        anomaly_persistence=1
    )

    positions = [
        (100, 100),
        (120, 100),
        (100, 100),
        (120, 100),
        (100, 100),
        (120, 100)
    ]

    result = None

    for x, y in positions:

        result = analyzer.update(
            object_id=1,
            x=x,
            y=y
        )

    assert result["status"] == "ANOMALY"

    assert (
        result["reason"]
        == "FREQUENT_DIRECTION_CHANGES"
    )


def test_anomaly_requires_persistence():
    analyzer = BehaviorAnalyzer(
        history_size=20,
        direction_change_threshold=2,
        minimum_movement=1,
        minimum_history=3,
        anomaly_persistence=3
    )

    positions = [
        (100, 100),
        (120, 100),
        (100, 100),
        (120, 100),
        (100, 100)
    ]

    results = []

    for x, y in positions:

        results.append(
            analyzer.update(
                object_id=1,
                x=x,
                y=y
            )
        )

    assert any(
        result["status"] == "NORMAL"
        for result in results
    )


def test_remove_cleans_object_state():
    analyzer = BehaviorAnalyzer()

    analyzer.update(
        object_id=1,
        x=100,
        y=100
    )

    analyzer.remove(
        active_ids=set()
    )

    assert 1 not in analyzer.history

    assert (
        1
        not in analyzer.anomaly_counters
    )