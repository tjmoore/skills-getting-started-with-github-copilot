"""
Tests for the Mergington High School API using AAA (Arrange-Act-Assert) pattern.

These tests use FastAPI's TestClient for synchronous requests and reset the
in-memory `activities` state before each test to ensure isolation.
"""

import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities mapping before each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_contains_expected_keys(client):
    # Arrange: fixture resets activities

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_adds_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    encoded = quote(activity, safe="")
    initial_count = len(activities[activity]["participants"])

    # Act
    resp = client.post(f"/activities/{encoded}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    assert len(activities[activity]["participants"]) == initial_count + 1


def test_prevent_duplicate_signup(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already present in initial data
    encoded = quote(activity, safe="")
    initial_count = len(activities[activity]["participants"])

    # Act
    resp = client.post(f"/activities/{encoded}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 400
    assert resp.json().get("detail") in ("Student already signed up for this activity", "Already registered")
    assert len(activities[activity]["participants"]) == initial_count


def test_signup_nonexistent_activity_returns_404(client):
    # Arrange
    activity = "No Such Club"
    email = "someone@mergington.edu"
    encoded = quote(activity, safe="")

    # Act
    resp = client.post(f"/activities/{encoded}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 404


def test_remove_participant_success(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    encoded = quote(activity, safe="")
    assert email in activities[activity]["participants"]

    # Act
    resp = client.delete(f"/activities/{encoded}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    # Arrange
    activity = "Chess Club"
    email = "noone@mergington.edu"
    encoded = quote(activity, safe="")

    # Act
    resp = client.delete(f"/activities/{encoded}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 404
