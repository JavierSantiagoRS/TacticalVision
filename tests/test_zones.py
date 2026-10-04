from src.zones import Zone


def test_point_inside_zone():
    zone = Zone(
        "ZONE_A",
        100,
        100,
        500,
        400
    )

    assert zone.contains(300, 250) is True


def test_point_outside_zone():
    zone = Zone(
        "ZONE_A",
        100,
        100,
        500,
        400
    )

    assert zone.contains(50, 50) is False


def test_zone_normalizes_coordinates():
    zone = Zone(
        "ZONE_A",
        500,
        400,
        100,
        100
    )

    assert zone.x1 == 100
    assert zone.y1 == 100
    assert zone.x2 == 500
    assert zone.y2 == 400