import os
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands

load_dotenv()

# Constants
UPDATE_INTERVAL = 60

WELCOME_MESSAGE = 'Welcome to YRHacks! Please verify your identity by clicking the button below.'
VERIFIED_MESSAGE = "Congrats, you are verified!"
UNVERIFIED_MESSAGE = "Sorry, we didn't recognize your username or tag. If you changed any one of them since your registration, please email us at yrhacks@gapps.yrdsb.ca."


class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.update_users.start()

    @tasks.loop(seconds=UPDATE_INTERVAL)
    async def update_users(self):
        """Updates list of approved users from the spreadsheet"""

        values = self.bot.get_cog('APIs').get_spreadsheet_data(
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

        if guild.system_channel is not None:
            await guild.system_channel.send(WELCOME_MESSAGE, view=VerificationView())


async def setup(bot):
    await bot.add_cog(Verification(bot))
