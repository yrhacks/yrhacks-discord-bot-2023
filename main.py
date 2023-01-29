import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import sched
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
creds = None
approved_users = []

# Authenticate Google Sheets API
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())


def get_approved_users():
    """Updates list of approved users from the spreadsheet"""

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=os.getenv('SPREADSHEET_ID'),
                                    range=os.getenv('SPREADSHEET_RANGE')).execute()
        values = result.get('values', [])
        approved_users = [value[0] for value in values]
        print(approved_users)
    except HttpError as err:
        print(err)


# Fetch new approved users every 60 seconds
approved_users_sched = sched.scheduler(time.time, time.sleep)
approved_users_sched.enter(60, 1, get_approved_users)
approved_users_sched.run()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run(os.getenv('DISCORD_TOKEN'))
