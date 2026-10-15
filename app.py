from flask import Flask, request
from datetime import datetime, timezone
import os
import requests

app = Flask(__name__)

@app.get("/votd")
def get_votd():

    # day query parameter and validation. no day defaults to today in UTC
    day = request.args.get("day")
    if day is None:
        today = datetime.now(timezone.utc)
        day_of_year = today.timetuple().tm_yday
        day = day_of_year
    elif not day.isdigit() or int(day) < 1 or int(day) > 366:
        return {
            "error": {
                "code": "INVALID_DAY",
                "message": "day must be an integer between 1 and 366"
            }
        }, 400
    else:
        day = int(day)

    # version query parameter and validation. no version defaults to 206
    version = request.args.get("version")
    if version is None:
        version = 206
    elif not version.isdigit() or int(version) < 1:
        return {
            "error": {
                "code": "INVALID_VERSION",
                "message": "version must be a positive integer"
            }
        }, 400
    else:
        version = int(version)

    api_key = os.getenv("YVP_APP_KEY")

    headers = {
        "X-YVP-App-Key": api_key
    }

    
    try:
        #first YouVersion API call to get the verse of the day
        votd_response = requests.get(
            f"https://api.youversion.com/v1/verse-of-the-days/{day}",
            headers = headers,
            timeout = 5
        )

        votd_response.raise_for_status()
        votd_data = votd_response.json()
        passage_id = votd_data["passage_id"]

        #second YouVersion API call to get the passage text
        passage_response = requests.get(
            f"https://api.youversion.com/v1/bibles/{version}/passages/{passage_id}",
            headers = headers,
            params = {"format": "text"},
            timeout = 5
        )

        passage_response.raise_for_status()
        passage_data = passage_response.json()

        response = {
            "day": day,
            "reference": passage_data["reference"],
            "text": passage_data["content"],
            "version_id": version
        }

    except requests.exceptions.RequestException:
        return {
            "error": {
                "code": "UPSTREAM_ERROR",
                "message": "Unable to retrieve passage"
            }
        }, 502

    except (KeyError, TypeError):
        return {
            "error": {
                "code": "UPSTREAM_ERROR",
                "message": "Invalid response from upstream API"
            }
        }, 502

    return response