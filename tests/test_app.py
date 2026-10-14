import app as api

def test_valid_day_and_version():
    client = api.app.test_client()

    response = client.get("/votd?day=100&version=206")

    assert response.status_code == 200
    assert response.get_json()["day"] == 100
    assert response.get_json()["version"] == 206

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