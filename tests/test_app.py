import app as api
from unittest.mock import patch

def test_valid_day_and_version():
    client = api.app.test_client()

    with patch("app.requests.get") as mock_get:

        # Simulate YouVersion's response
        mock_get.return_value.json.return_value = {
            "day": 195,
            "passage_id": "REV.3.20"
        }

        response = client.get("/votd?day=195&version=206")

        assert response.status_code == 200
        assert response.get_json()["day"] == 195
        assert response.get_json()["version"] == 206
        assert response.get_json()["passage_id"] == "REV.3.20"

        mock_get.assert_called_once()

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