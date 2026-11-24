import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activity_data(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["student@example.com"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Wednesdays",
            "max_participants": 15,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activity_data):
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_list_activities(client):
    # Arrange
    expected = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["student@example.com"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Wednesdays",
            "max_participants": 15,
            "participants": [],
        },
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == expected


def test_list_activities_when_empty(client, activity_data):
    # Arrange
    activity_data.clear()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {}
    assert response.headers["cache-control"] == "no-store"


def test_list_activities_reflects_changes(client, activity_data):
    # Arrange
    initial = client.get("/activities")
    activity_data["Chess Club"]["participants"].append("another@example.com")

    # Act
    refreshed = client.get("/activities")

    # Assert
    assert initial.status_code == 200
    assert initial.json()["Chess Club"]["participants"] == ["student@example.com"]
    assert refreshed.status_code == 200
    assert refreshed.headers["cache-control"] == "no-store"
    assert refreshed.json()["Chess Club"]["participants"] == [
        "student@example.com",
        "another@example.com",
    ]
