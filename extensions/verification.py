import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import googleapiclient.discovery

load_dotenv()

# Constants
WELCOME_MESSAGE = "Please verify your identity and gain access to the server by clicking the button below."
VERIFIED_MESSAGE = "Congrats, you are verified!"
UNVERIFIED_MESSAGE = "Sorry, we didn't recognize your username or tag. If you changed any one of them since your registration, please email us at yrhacks@gapps.yrdsb.ca."


class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.build_service()
        self.update_users.start()

    def cog_unload(self):
        self.update_users.cancel()

    def generate_auth_data(
            self,
            client_email: str,
            private_key_id,
            private_key,
            project_id):
        return {
            'client_email': client_email,
            'private_key_id': private_key_id,
            'private_key': private_key.replace('\\n', '\n'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            'project_id': project_id
        }

    def build_service(self):
        auth_data = self.generate_auth_data(
            os.getenv('CLIENT_EMAIL'),
            os.getenv('PRIVATE_KEY_ID'),
            os.getenv('PRIVATE_KEY'),
            os.getenv('PROJECT_ID'),
        )
        credentials = service_account.Credentials.from_service_account_info(
            auth_data)
        self.sheets_service = googleapiclient.discovery.build(
            'sheets', 'v4', credentials=credentials)

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

    @tasks.loop(seconds=60)
    async def update_users(self):
        """Updates list of approved users from the spreadsheet"""

        values = self.get_spreadsheet_data(
            os.getenv('SPREADSHEET_ID'), os.getenv('SPREADSHEET_DISCORD_RANGE'))
        self.approved_users = [value[0] for value in values]

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id='verify')
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.guild
        verified_role = discord.utils.get(
            server.roles, name=os.getenv('VERIFIED_ROLE_NAME'))
        if verified_role in interaction.user.roles:
            await interaction.response.send_message("You're already verified!", ephemeral=True)
        elif f'{interaction.user.name}#{interaction.user.discriminator}' in self.approved_users:
            # Add role to user
            await interaction.user.add_roles(verified_role)
            await interaction.response.send_message(VERIFIED_MESSAGE, ephemeral=True)
        else:
            await interaction.response.send_message(UNVERIFIED_MESSAGE, ephemeral=True)


class Verification(commands.Cog):
    """Cog for verification commands and tasks"""

    def __init__(self, bot):
        self.bot = bot

    async def setup_hook(self) -> None:
        self.bot.add_view(VerificationView())

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Send welcome message and verification button"""

        if guild.rules_channel is not None:
            await guild.rules_channel.send(WELCOME_MESSAGE, view=VerificationView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_join_button(self, ctx):
        """Send welcome message and verification button"""

        if ctx.guild.rules_channel is not None:
            await ctx.guild.rules_channel.send(WELCOME_MESSAGE, view=VerificationView())


async def setup(bot):
    await bot.add_cog(Verification(bot))
