import app as api
from unittest.mock import patch, Mock
import requests

def test_valid_day_and_version(monkeypatch):
    monkeypatch.setenv("YVP_APP_KEY", "fake-test-key")
    client = api.app.test_client()

    # Fake response for first API call
    votd_response = Mock()
    votd_response.json.return_value = {
        "day": 195,
        "passage_id": "REV.3.20"
    }

    # Fake response for second API call
    passage_response = Mock()
    passage_response.json.return_value = {
        "reference": "Revelation 3:20",
        "content": "Sample scripture text"
    }

    with patch("app.requests.get") as mock_get:

        mock_get.side_effect = [
            votd_response,
            passage_response
        ]

        response = client.get("/votd?day=195&version=206")

        assert response.status_code == 200

        assert response.get_json() == {
            "day": 195,
            "reference": "Revelation 3:20",
            "text": "Sample scripture text",
            "version_id": 206
        }

        assert mock_get.call_count == 2

def test_invalid_day():
    client = api.app.test_client()

    response = client.get("/votd?day=0")

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_DAY"

def test_invalid_version():
    client = api.app.test_client()

    response = client.get("/votd?version=0")

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_VERSION"

def test_upstream_timeout(monkeypatch):
    client = api.app.test_client()

    monkeypatch.setenv("YVP_APP_KEY", "fake-test-key")

    with patch("app.requests.get") as mock_get:

        mock_get.side_effect = requests.exceptions.Timeout()

        response = client.get("/votd?day=195")

        assert response.status_code == 502
        assert response.get_json()["error"]["code"] == "UPSTREAM_ERROR" 

def test_missing_passage_id(monkeypatch):
    client = api.app.test_client()

    monkeypatch.setenv("YVP_APP_KEY", "fake-test-key")

    fake_response = Mock()
    fake_response.json.return_value = {
        "day": 195
    }

    with patch("app.requests.get", return_value=fake_response) as mock_get:
        response = client.get("/votd?day=195")

        assert response.status_code == 502
        assert response.get_json()["error"]["code"] == "UPSTREAM_ERROR"

        mock_get.assert_called_once()

def test_invalid_passage_content(monkeypatch):
    client = api.app.test_client()
    monkeypatch.setenv("YVP_APP_KEY", "fake-test-key")

    # First API returns valid passage ID
    votd_response = Mock()
    votd_response.json.return_value = {
        "passage_id": "REV.3.20"
    }

    # Second API returns invalid content
    passage_response = Mock()
    passage_response.json.return_value = {
        "reference": "Revelation 3:20",
        "content": None
    }

    with patch("app.requests.get") as mock_get:
        mock_get.side_effect = [
            votd_response,
            passage_response
            ]

        response = client.get("/votd?day=195")

        assert response.status_code == 502
        assert response.get_json()["error"]["code"] == "UPSTREAM_ERROR"
        assert mock_get.call_count == 2