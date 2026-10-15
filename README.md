# Project A - Verse of the Day API
Kegan Silk

## Overview:
A REST API built with Python and Flask that retrieves the Verse of the Day from the YouVersion API. The application combines two YouVersion API requests into a single JSON response containing the day, scripture reference, passage text, and Bible version ID.

### Requirements
- Python 3.10 or newer
- A YouVersion API key with access to the requested Bible translation
- Dependencies listed in requirements.txt


## Setup & Run Instructions
### Installation
1. Clone the repository and open the project folder.
2. Create and activate a virtual environment.
Windows (PowerShell):
```
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
macOS/Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```
3. Install dependencies.
```
python -m pip install -r requirements.txt
```
4. Configure your YouVersion API key.

The application reads the API key from the YVP_APP_KEY environment variable. API keys are not stored in the source code or committed to Git.

Windows (PowerShell):
```
$env:YVP_APP_KEY = "your-api-key"
```
macOS/Linux:
```
export YVP_APP_KEY="your-api-key"
```
These commands set the variable for the current terminal session.

### Running the Application

Start the Flask development server:
```
python -m flask --app app run
```
The API will be available at:

http://127.0.0.1:5000/votd

The Flask development server is intended for local testing and should not be exposed publicly.

#### Example Request
```
GET /votd?day=195&version=206
```
A successful response returns the following structure:
```
{
  "day": 195,
  "reference": "Revelation 3:20",
  "text": "Example passage text",
  "version_id": 206
}
```
The example text is a placeholder. Actual passage content is retrieved from YouVersion.

Both parameters are optional. Without them, the API uses the current UTC day of the year and Bible version 206.

### Running the Tests

Run all automated tests from the project root:

python -m pytest -v

Tests use pytest and Python's unittest.mock library to simulate YouVersion responses. This allows testing of successful requests, validation, error handling, and caching without contacting the real YouVersion API.

## Decisions and Assumptions

Flask: I chose Flask because it is lightweight and provides everything needed for a small API without additional complexity.

YouVersion endpoint: The provided START-HERE instructions used verse_of_the_days, but the working YouVersion endpoint uses verse-of-the-days. I used the hyphenated endpoint after confirming it returned a successful HTTP 200 response.

Default day and version: When no day is provided, the API uses the current UTC day of the year. I chose UTC for consistency regardless of the server's location. This means the day changes at midnight UTC, which may be earlier than midnight for users in other time zones.

The default Bible version is 206, the World English Bible, because it is a public-domain translation and a reasonable default for this project.

Input validation: Days must be integers from 1 through 366. Day 366 is accepted even in non-leap years because the endpoint accepts a day number rather than a specific calendar date. Leading zeros, such as 007, are accepted and converted to 7, while values like +7 are rejected.

Bible versions must be positive integers. The API does not verify whether a version exists during input validation. Instead, it passes the version ID to YouVersion and handles any resulting upstream error.

Error handling: The API returns consistent JSON error responses rather than exposing raw upstream errors.

| Status | Error Code | Meaning |
|--------|------------|---------|
| 400 | `INVALID_DAY` | Invalid day parameter |
| 400 | `INVALID_VERSION` | Invalid version parameter |
| 500 | `CONFIG_ERROR` | API key is missing when an upstream lookup is needed |
| 502 | `UPSTREAM_ERROR` | YouVersion request failed or returned invalid data |

Unavailable, unauthorized, or nonexistent Bible versions that produce upstream HTTP errors currently result in a 502 response. I chose to keep upstream error handling simple rather than add separate cases for each possible YouVersion response.

The API key is checked when a request needs to contact YouVersion, rather than preventing the application from starting without it. This also allows requests already stored in the cache to be served without another upstream call.

In-memory caching: I used a Python dictionary with (day, version) as the cache key. This avoids making duplicate API requests for the same passage and translation.

Only successful responses are cached. The cache is limited to the current process, does not expire automatically, and has no maximum size. I felt this was sufficient for the small scope of the project without introducing additional dependencies.

Mocked testing: I used pytest with unittest.mock to simulate responses from YouVersion. This keeps automated tests consistent, avoids unnecessary external requests, and makes it possible to test failures such as timeouts and missing data.

## What I'd Do Next

Given more time or a larger production scope, I would consider:
- Adding cache expiration and size limits.
- Making the default Bible version configurable.
- Separating validation and API requests into helper functions as the application grows.
- Providing clearer errors for unavailable or unauthorized Bible versions.
- Adding logging for debugging upstream failures.




