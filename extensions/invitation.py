import os
from dotenv import load_dotenv
from discord.ext import commands
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly',
          'https://www.googleapis.com/auth/gmail.compose']
MESSAGE = """<html>
  <body>
    <p>Hello there,<br>
    You are receiving this email because you registered for YRHacks 2023! Below is the invitation for the YRHacks Discord server. Please click the link below to join the server.
    <br><br> 
    This is a one-time use link. Do not share the link with anyone else.<br> 
    If you did not register for YRHacks 2023, please ignore this email.<br> 
    <br>
    Join: <a href={link}>{link}</a><br> 
    <br> 
    See you at YRHacks 2023!<br> 
    The YRHacks Team</p>
  </body>
</html>"""
FROM = "yrhacks@gapps.yrdsb.ca"
SUBJECT = "YRHacks Discord Server Invitation"


class Invitation(commands.Cog):
    """Cog for generating one-time invitation links and emailing them"""

    def __init__(self, bot):
        self.bot = bot
        self.drafts = []

    def build_services(self):
        """Authenticate Google Sheets API"""

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
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
        self.gmail_service = build('gmail', 'v1', credentials=creds)
        self.sheets_service = build('sheets', 'v4', credentials=creds)

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

    async def generate_invite_link(self, ctx):
        """Generate a one-time invite link"""
        channel = ctx.channel
        invite = await channel.create_invite(max_uses=1)
        return invite.url

    async def create_draft(self, ctx, email_address):
        """Create a draft invitation link for a member"""

        link = await self.generate_invite_link(ctx)
        message = MIMEText(MESSAGE.format(link=link), "html")

        message['To'] = email_address
        message['From'] = FROM
        message['Subject'] = SUBJECT

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'message': {
                'raw': encoded_message
            }
        }

        # Create draft
        draft = self.gmail_service.users().drafts().create(userId="me",
                                                           body=create_message).execute()
        self.drafts.append(draft)

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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_drafts(self, ctx):
        """Create drafts for all members"""

        self.build_services()

        values = self.get_spreadsheet_data(
            os.getenv('SPREADSHEET_ID'), os.getenv('SPREADSHEET_EMAIL_RANGE'))
        emails = [value[0] for value in values]

        for email in emails:
            await self.create_draft(ctx, email)

        # Send confirmation message
        await ctx.send(f"{len(emails)} drafts created.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def send_drafts(self, ctx):
        """Send all drafts to their respective members"""

        # Send drafts
        apis_cog = self.bot.get_cog('APIs')
        for draft in self.drafts:
            apis_cog.send_draft(draft)

        # Send confirmation message
        await ctx.send(f"{len(self.drafts)} emails sent.")

        # Clear drafts
        self.drafts = []


async def setup(bot):
    await bot.add_cog(Invitation(bot))
