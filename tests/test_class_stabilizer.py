import pytest

from src.class_stabilizer import ClassStabilizer


def test_initial_observation_returns_current_class():

    stabilizer = ClassStabilizer(
        history_size=5,
        minimum_observations=3
    )

    result = stabilizer.update(
        1,
        "person"
    )

    assert result == "person"


def test_majority_class_is_selected():

    stabilizer = ClassStabilizer(
        history_size=5,
        minimum_observations=3
    )

    stabilizer.update(1, "person")
    stabilizer.update(1, "person")
    result = stabilizer.update(1, "remote")

    assert result == "person"


def test_history_is_limited():

    stabilizer = ClassStabilizer(
        history_size=3,
        minimum_observations=1
    )

    stabilizer.update(1, "person")
    stabilizer.update(1, "person")
    stabilizer.update(1, "remote")
    stabilizer.update(1, "remote")

    assert len(
        stabilizer.histories[1]
    ) == 3


def test_get_returns_stabilized_class():

    stabilizer = ClassStabilizer(
        history_size=5,
        minimum_observations=1
    )

    stabilizer.update(1, "person")
    stabilizer.update(1, "person")
    stabilizer.update(1, "remote")

    assert (
        stabilizer.get(1)
        == "person"
    )


def test_remove_stale_histories():

    stabilizer = ClassStabilizer()

    stabilizer.update(1, "person")
    stabilizer.update(2, "vehicle")

    stabilizer.remove({2})

    assert 1 not in stabilizer.histories
    assert 2 in stabilizer.histories


def test_clear():

    stabilizer = ClassStabilizer()

    stabilizer.update(1, "person")
    stabilizer.update(2, "vehicle")

    stabilizer.clear()

    assert stabilizer.histories == {}


def test_invalid_history_size():

    with pytest.raises(ValueError):

        ClassStabilizer(
            history_size=0
        )


def test_invalid_minimum_observations():

    with pytest.raises(ValueError):

        ClassStabilizer(
            history_size=2,
            minimum_observations=3
        )