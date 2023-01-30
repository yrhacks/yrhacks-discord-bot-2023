import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import threading

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'
UPDATE_INTERVAL = 60
WELCOME_MESSAGE = 'Welcome to YRHacks! Please verify your identity by clicking the button below.'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
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
    """Updates list of approved users from the spreadsheet on an interval"""
    global approved_users
    threading.Timer(UPDATE_INTERVAL, get_approved_users).start()
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=os.getenv('SPREADSHEET_ID'),
                                    range=os.getenv('SPREADSHEET_RANGE')).execute()
        values = result.get('values', [])
        approved_users = [value[0] for value in values]
    except HttpError as err:
        print(err)


get_approved_users()


class Buttons(discord.ui.View):
    # Verification button
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.guild
        verified_role = discord.utils.get(
            server.roles, name=os.getenv('VERIFIED_ROLE_NAME'))

        if f'{interaction.user.name}#{interaction.user.discriminator}' in approved_users:
            # Add role to user
            await interaction.user.add_roles(verified_role)
            await interaction.response.send_message("Congrats, you are verified!", ephemeral=True)
        else:
            await interaction.response.send_message("Sorry, we didn't recognize your username or tag. If you changed any one of them since your registration, please email us at yrhacks@gapps.yrdsb.ca.", ephemeral=True)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_guild_join(guild):
    # Send welcome message and verification button
    if guild.system_channel is not None:
        view = Buttons()
        await guild.system_channel.send(WELCOME_MESSAGE, view=view)

bot.run(os.getenv('DISCORD_TOKEN'))
