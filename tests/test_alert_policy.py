import pytest

from src.alert_policy import AlertPolicy


def test_normal_priority_is_normal():

    policy = AlertPolicy()

    assert (
        policy.evaluate("NORMAL")
        == "NORMAL"
    )


def test_low_priority_is_normal():

    policy = AlertPolicy()

    assert (
        policy.evaluate("LOW")
        == "NORMAL"
    )


def test_medium_priority_is_suspicious():

    policy = AlertPolicy()

    assert (
        policy.evaluate("MEDIUM")
        == "SUSPICIOUS"
    )


def test_high_priority_is_alert():

    policy = AlertPolicy()

    assert (
        policy.evaluate("HIGH")
        == "ALERT"
    )


def test_invalid_priority_raises_error():

    policy = AlertPolicy()

    with pytest.raises(ValueError):

        policy.evaluate(
            "UNKNOWN"
        )