from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "TacticalVision"
    assert data["status"] == "online"


def test_status():

    response = client.get(
        "/api/status"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "online"


def test_events():

    response = client.get(
        "/api/events"
    )

    assert response.status_code == 200
    assert isinstance(
        response.json(),
        list
    )


def test_event_count():

    response = client.get(
        "/api/events/count"
    )

    assert response.status_code == 200

    assert "total" in response.json()


def test_event_types():

    response = client.get(
        "/api/events/types"
    )

    assert response.status_code == 200
    assert isinstance(
        response.json(),
        list
    )