from src.motion import MotionAnalyzer


def test_first_observation():

    analyzer = MotionAnalyzer()

    result = analyzer.update(
        object_id=1,
        x=100,
        y=100
    )

    assert result["direction"] == "STATIONARY"
    assert result["speed"] == 0.0
    assert result["state"] == "STATIONARY"
    assert result["distance"] == 0.0


def test_east_movement():

    analyzer = MotionAnalyzer()

    analyzer.update(
        object_id=1,
        x=100,
        y=100
    )

    result = analyzer.update(
        object_id=1,
        x=110,
        y=100
    )

    assert result["direction"] == "EAST"
    assert result["state"] == "MOVING"
    assert result["delta_x"] == 10
    assert result["delta_y"] == 0


def test_west_movement():

    analyzer = MotionAnalyzer()

    analyzer.update(
        object_id=1,
        x=100,
        y=100
    )

    result = analyzer.update(
        object_id=1,
        x=90,
        y=100
    )

    assert result["direction"] == "WEST"
    assert result["state"] == "MOVING"


def test_north_movement():

    analyzer = MotionAnalyzer()

    analyzer.update(
        object_id=1,
        x=100,
        y=100
    )

    result = analyzer.update(
        object_id=1,
        x=100,
        y=90
    )

    assert result["direction"] == "NORTH"


def test_south_movement():

    analyzer = MotionAnalyzer()

    analyzer.update(
        object_id=1,
        x=100,
        y=100
    )

    result = analyzer.update(
        object_id=1,
        x=100,
        y=110
    )

    assert result["direction"] == "SOUTH"


def test_diagonal_distance():

    analyzer = MotionAnalyzer()

    analyzer.update(
        object_id=1,
        x=0,
        y=0
    )

    result = analyzer.update(
        object_id=1,
        x=3,
        y=4
    )

    assert result["distance"] == 5.0