import os
from dotenv import load_dotenv
from discord.ext import commands
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly',
          'https://www.googleapis.com/auth/gmail.compose']


class APIs(commands.Cog):
    """Cog for interacting with Google APIs"""

    def __init__(self, bot):
        self.bot = bot
        self.build_services(SCOPES)

    def build_services(self, scopes):
        """Authenticate Google Sheets API"""

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        # Build the services
        self.sheets_service = build('sheets', 'v4', credentials=creds)
        self.gmail_service = build('gmail', 'v1', credentials=creds)

    def get_spreadsheet_data(self, sheet_id, sheet_range):
        """Get data from a Google Sheets spreadsheet"""

        try:
            # Call the Sheets API
            result = self.sheets_service.spreadsheets().values().get(spreadsheetId=sheet_id,
                                                                     range=sheet_range).execute()
            values = result.get('values', [])
            return values
        except HttpError as err:
            print(err)

    def create_draft(self, create_message):
        """Create a gmail draft"""

        try:
            draft = self.gmail_service.users().drafts().create(userId="me",
                                                               body=create_message).execute()
        except HttpError as error:
            print(F'An error occurred: {error}')
            draft = None

        return draft

    def send_draft(self, draft):
        """Send a gmail draft"""

        try:
            self.gmail_service.users().drafts().send(userId="me", body=draft).execute()
        except HttpError as error:
            print(F'An error occurred: {error}')


async def setup(bot):
    await bot.add_cog(APIs(bot))
