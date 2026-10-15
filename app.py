from flask import Flask, request
from datetime import datetime, timezone
import os
import requests

cache = {}

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

    cache_key = (day, version)

    api_key = os.getenv("YVP_APP_KEY")

    #check for missing API key
    if not api_key:
        return {
            "error": {
                "code": "CONFIG_ERROR",
                "message": "API key is not configured"
            }
        }, 500

    if cache_key in cache:
            return cache[cache_key]

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
        # Validate passage_id (ensure it's a non-empty string)
        if not isinstance(passage_id, str) or not passage_id.strip():
            raise ValueError("Invalid passage ID")

        #second YouVersion API call to get the passage text
        passage_response = requests.get(
            f"https://api.youversion.com/v1/bibles/{version}/passages/{passage_id}",
            headers = headers,
            params = {"format": "text"},
            timeout = 5
        )

        passage_response.raise_for_status()
        passage_data = passage_response.json()

       # Extract passage reference and text
        reference = passage_data["reference"]
        content = passage_data["content"]

        # Validate passage reference
        if not isinstance(reference, str) or not reference.strip():
            raise ValueError("Invalid passage reference")

        # Validate passage content
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Invalid passage content")

        # Construct the final response
        response = {
            "day": day,
            "reference": reference,
            "text": content,
            "version_id": version
        }

    except requests.exceptions.RequestException:
        return {
            "error": {
                "code": "UPSTREAM_ERROR",
                "message": "Unable to retrieve passage"
            }
        }, 502

    except (KeyError, TypeError, ValueError):
        return {
            "error": {
                "code": "UPSTREAM_ERROR",
                "message": "Invalid response from upstream API"
            }
        }, 502

    cache[cache_key] = response
    return response