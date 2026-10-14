from flask import Flask, request
from datetime import datetime, timezone

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

    return {"day": day, "version": version}