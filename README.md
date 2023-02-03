# YRHacks Discord Bot 2023

Discord bot for verification of members and mentor requests. Approved users are taken from a Google Sheet.

## How to Set It Up

### Google Sheets

- Create a Google Sheet linked to registration form, should have the Discord usernames + tags and emails of registered students
- Go to the YRHacks Discord Bot app in yrhacks@gapps.yrdsb.ca's Google Cloud
- Save the Auth 2.0 Client ID as `credentials.json` in the project directory

### Running Locally

- Make a `.env` using `.env.sample` as a template
- `pip install -r requirements.txt`
- `python3 main.py`
