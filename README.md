# YRHacks Discord Bot 2023

Discord bot for verification of members and mentor requests. Approved users are taken from a Google Sheet.

## How to Set It Up

### Google Sheets

- Create a Google Sheet with the Discord usernames and tags of registered students
- Create a Google Cloud service account with the Google Sheets API
- Generate an API key and save the JSON as `credentials.json` in the project directory

### Running Locally

- Make a `.env` using `.env.sample` as a template
- `pip install -r requirements.txt`
- `python3 main.py`
