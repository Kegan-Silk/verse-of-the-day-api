import app as api
from unittest.mock import patch, Mock

def test_valid_day_and_version():
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