import os
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'
UPDATE_INTERVAL = 60

WELCOME_MESSAGE = 'Welcome to YRHacks! Please verify your identity by clicking the button below.'
VERIFIED_MESSAGE = "Congrats, you are verified!"
UNVERIFIED_MESSAGE = "Sorry, we didn't recognize your username or tag. If you changed any one of them since your registration, please email us at yrhacks@gapps.yrdsb.ca."


class Verification(commands.Cog):
    """Cog for verification commands and tasks"""

    class VerificationButton(discord.ui.Button):
        """Button that verifies users when clicked"""

        def __init__(self, approved_users):
            super().__init__(label="Verify", style=discord.ButtonStyle.green)
            self.approved_users = approved_users

        async def callback(self, interaction: discord.Interaction):
            server = interaction.guild
            verified_role = discord.utils.get(
                server.roles, name=os.getenv('VERIFIED_ROLE_NAME'))

            if f'{interaction.user.name}#{interaction.user.discriminator}' in self.approved_users:
                # Add role to user
                await interaction.user.add_roles(verified_role)
                await interaction.response.send_message(VERIFIED_MESSAGE, ephemeral=True)
            else:
                await interaction.response.send_message(UNVERIFIED_MESSAGE, ephemeral=True)

    def __init__(self, bot):
        self.bot = bot
        self.approved_users = []
        self.auth_google_api()
        self.update_users.start()

    def cog_unload(self):
        self.update_users.cancel()

    def auth_google_api(self):
        """Authenticate Google Sheets API"""

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(
                TOKEN_FILE, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())

    @tasks.loop(seconds=UPDATE_INTERVAL)
    async def update_users(self):
        """Updates list of approved users from the spreadsheet"""

        try:
            service = build('sheets', 'v4', credentials=self.creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=os.getenv('SPREADSHEET_ID'),
                                        range=os.getenv('SPREADSHEET_RANGE')).execute()
            values = result.get('values', [])
            self.approved_users = [value[0] for value in values]
        except HttpError as err:
            print(err)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Send welcome message and verification button"""

        if guild.system_channel is not None:
            view = discord.ui.View()
            button = self.VerificationButton(self.approved_users)
            view.add_item(button)
            await guild.system_channel.send(WELCOME_MESSAGE, view=view)

    @commands.command()
    async def test(self, ctx):
        """Test command"""

        await self.on_guild_join(ctx.guild)


async def setup(bot):
    await bot.add_cog(Verification(bot))
