from src.event_engine import EventEngine
from src.zones import Zone


def create_zone():
    return Zone(
        name="TEST_ZONE",
        x1=100,
        y1=100,
        x2=200,
        y2=200
    )


def test_enter_event():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    # Object starts outside.
    engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    # Object enters zone.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "ENTER"
    assert event["object_id"] == 1
    assert event["object_class"] == "person"
    assert event["zone"] == "TEST_ZONE"


def test_exit_event():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    # Object starts inside.
    engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    # Object exits zone.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "EXIT"
    assert event["object_id"] == 1
    assert event["object_class"] == "person"
    assert event["zone"] == "TEST_ZONE"


def test_no_event_while_object_remains_inside():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    # First frame: outside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is None

    # Second frame: enters.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "ENTER"

    # Third frame: remains inside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=160,
        y=160,
        zone=zone
    )

    assert event is None


def test_no_event_while_object_remains_outside():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    # First frame: outside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is None

    # Second frame: still outside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=60,
        y=60,
        zone=zone
    )

    assert event is None


def test_enter_then_exit():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    # Outside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is None

    # Enter.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "ENTER"

    # Exit.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "EXIT"


def test_event_contains_motion_context():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    # Object starts outside.
    engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    # Object enters with motion information.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone,
        confidence=0.92,
        direction="RIGHT",
        speed=145.5
    )

    assert event is not None
    assert event["type"] == "ENTER"
    assert event["object_id"] == 1
    assert event["object_class"] == "person"
    assert event["zone"] == "TEST_ZONE"
    assert event["confidence"] == 0.92
    assert event["direction"] == "RIGHT"
    assert event["speed"] == 145.5


def test_event_without_optional_motion_data():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event is not None
    assert event["confidence"] is None
    assert event["direction"] is None
    assert event["speed"] is None


def test_object_can_enter_and_exit_multiple_times():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    # Outside.
    assert engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    ) is None

    # ENTER.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event["type"] == "ENTER"

    # Remains inside.
    assert engine.update(
        object_id=1,
        object_class="person",
        x=160,
        y=160,
        zone=zone
    ) is None

    # EXIT.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event["type"] == "EXIT"

    # ENTER again.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event["type"] == "ENTER"

    # EXIT again.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event["type"] == "EXIT"


def test_multiple_objects_have_independent_states():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    # Object 1 enters.
    event_1 = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event_1 is not None
    assert event_1["type"] == "ENTER"
    assert event_1["object_id"] == 1

    # Object 2 enters independently.
    event_2 = engine.update(
        object_id=2,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event_2 is not None
    assert event_2["type"] == "ENTER"
    assert event_2["object_id"] == 2

    # Object 1 exits.
    event_1 = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event_1 is not None
    assert event_1["type"] == "EXIT"
    assert event_1["object_id"] == 1

    # Object 2 remains inside.
    event_2 = engine.update(
        object_id=2,
        object_class="person",
        x=160,
        y=160,
        zone=zone
    )

    assert event_2 is None


def test_multiple_zones_have_independent_states():
    zone_1 = Zone(
        name="ZONE_1",
        x1=100,
        y1=100,
        x2=200,
        y2=200
    )

    zone_2 = Zone(
        name="ZONE_2",
        x1=300,
        y1=300,
        x2=400,
        y2=400
    )

    engine = EventEngine(confirmation_frames=1)

    # Object enters zone 1.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone_1
    )

    assert event is not None
    assert event["type"] == "ENTER"
    assert event["zone"] == "ZONE_1"

    # Same object enters zone 2 independently.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=350,
        y=350,
        zone=zone_2
    )

    assert event is not None
    assert event["type"] == "ENTER"
    assert event["zone"] == "ZONE_2"


def test_boundary_inside_behavior():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    # Test the exact top-left boundary.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=100,
        y=100,
        zone=zone
    )

    # The expected result depends on Zone.contains().
    if zone.contains(100, 100):
        assert event is not None
        assert event["type"] == "ENTER"
    else:
        assert event is None


def test_event_preserves_object_class():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    engine.update(
        object_id=42,
        object_class="cell phone",
        x=50,
        y=50,
        zone=zone
    )

    event = engine.update(
        object_id=42,
        object_class="cell phone",
        x=150,
        y=150,
        zone=zone
    )

    assert event is not None
    assert event["object_id"] == 42
    assert event["object_class"] == "cell phone"


def test_event_preserves_zero_motion_values():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone,
        confidence=0.0,
        direction="UNKNOWN",
        speed=0.0
    )

    assert event is not None
    assert event["confidence"] == 0.0
    assert event["direction"] == "UNKNOWN"
    assert event["speed"] == 0.0


# ============================================================
# CONFIRMATION TESTS
# ============================================================


def test_enter_requires_confirmation_frames():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=3)

    # Object starts outside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is None

    # First consecutive frame inside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event is None

    # Second consecutive frame inside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=160,
        y=160,
        zone=zone
    )

    assert event is None

    # Third consecutive frame inside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=170,
        y=170,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "ENTER"
    assert event["object_id"] == 1


def test_exit_requires_confirmation_frames():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=3)

    # Establish the object as inside.
    engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    # Confirm the initial ENTER state.
    engine.update(
        object_id=1,
        object_class="person",
        x=160,
        y=160,
        zone=zone
    )

    engine.update(
        object_id=1,
        object_class="person",
        x=170,
        y=170,
        zone=zone
    )

    # First frame outside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is None

    # Second frame outside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=60,
        y=60,
        zone=zone
    )

    assert event is None

    # Third frame outside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=70,
        y=70,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "EXIT"
    assert event["object_id"] == 1


def test_unstable_transition_is_cancelled():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=3)

    # Object starts outside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is None

    # Object enters for only one frame.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event is None

    # Object immediately returns outside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is None

    # Object enters again.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event is None

    # Second consecutive frame inside.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=160,
        y=160,
        zone=zone
    )

    assert event is None

    # Third consecutive frame confirms ENTER.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=170,
        y=170,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "ENTER"


def test_confirmation_resets_when_object_returns_to_previous_state():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=3)

    # Establish outside state.
    engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    # Begin ENTER transition.
    engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    engine.update(
        object_id=1,
        object_class="person",
        x=160,
        y=160,
        zone=zone
    )

    # Return outside before confirmation.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is None

    # Start a completely new ENTER transition.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event is None

    # Second frame.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=160,
        y=160,
        zone=zone
    )

    assert event is None

    # Third frame confirms it.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=170,
        y=170,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "ENTER"


def test_confirmation_preserves_motion_context():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=3)

    # Outside.
    engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    # First frame inside.
    engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone,
        confidence=0.80,
        direction="RIGHT",
        speed=100.0
    )

    # Second frame inside.
    engine.update(
        object_id=1,
        object_class="person",
        x=160,
        y=160,
        zone=zone,
        confidence=0.85,
        direction="RIGHT",
        speed=110.0
    )

    # Third frame confirms ENTER.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=170,
        y=170,
        zone=zone,
        confidence=0.92,
        direction="RIGHT",
        speed=120.0
    )

    assert event is not None
    assert event["type"] == "ENTER"
    assert event["confidence"] == 0.92
    assert event["direction"] == "RIGHT"
    assert event["speed"] == 120.0


def test_confirmation_works_independently_for_multiple_objects():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=3)

    # Object 1 starts inside.
    engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    engine.update(
        object_id=1,
        object_class="person",
        x=160,
        y=160,
        zone=zone
    )

    event = engine.update(
        object_id=1,
        object_class="person",
        x=170,
        y=170,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "ENTER"
    assert event["object_id"] == 1

    # Object 2 starts outside.
    engine.update(
        object_id=2,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    # Object 2 begins entering.
    event = engine.update(
        object_id=2,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event is None

    # Object 1 exits and should be independent of object 2.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is None

    # Object 2 continues its own confirmation.
    engine.update(
        object_id=2,
        object_class="person",
        x=160,
        y=160,
        zone=zone
    )

    event = engine.update(
        object_id=2,
        object_class="person",
        x=170,
        y=170,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "ENTER"
    assert event["object_id"] == 2


def test_invalid_confirmation_frames():
    for value in (0, -1, -5):
        try:
            EventEngine(
                confirmation_frames=value
            )
            assert False, (
                "Expected ValueError for "
                f"confirmation_frames={value}"
            )
        except ValueError:
            pass


def test_remove_clears_object_state():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=3)

    # Create pending state.
    engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert (
        1,
        "TEST_ZONE"
    ) in engine.pending_states

    # Remove tracked object.
    engine.remove(set())

    assert (
        1,
        "TEST_ZONE"
    ) not in engine.previous_states

    assert (
        1,
        "TEST_ZONE"
    ) not in engine.pending_states

    assert (
        1,
        "TEST_ZONE"
    ) not in engine.pending_counts


def test_confirmation_one_behaves_like_immediate_transition():
    zone = create_zone()
    engine = EventEngine(confirmation_frames=1)

    # Outside.
    engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    # ENTER must happen immediately.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=150,
        y=150,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "ENTER"

    # EXIT must also happen immediately.
    event = engine.update(
        object_id=1,
        object_class="person",
        x=50,
        y=50,
        zone=zone
    )

    assert event is not None
    assert event["type"] == "EXIT"
