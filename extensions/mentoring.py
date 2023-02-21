import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord import app_commands
import traceback
import textwrap

load_dotenv()


class RequestView(discord.ui.View):
    def __init__(self, requester: discord.Interaction.user, request_subject):
        super().__init__(timeout=None)
        self.requester = requester
        self.request_subject = request_subject

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id='accept')
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel_name = f"{interaction.user.name} - {self.requester.name} - {self.request_subject}"
        mentoring_category = interaction.guild.get_channel(
            int(os.getenv('MENTORING_CATEGORY_ID')))
        channel = await interaction.guild.create_text_channel(
            name=channel_name, category=mentoring_category)

        await channel.send(textwrap.dedent(f"""
        Hello, {self.requester.mention}! {interaction.user.mention} has accepted your request for help concerning {self.request_subject}!
        Please use this channel to discuss your questions and concerns.
        """))

        button.disabled = True


class RequestModal(discord.ui.Modal, title="Mentor Request"):
    subject_input = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Brief subject of interest",
        required=True,
        placeholder="e.g. C++, React"
    )

    async def on_submit(self, interaction: discord.Interaction):
        requests_channel = interaction.guild.get_channel(
            int(os.getenv('REQUESTS_CHANNEL_ID')))
        request_string = f"""
        Request from {interaction.user.mention}
        Subject: {self.subject_input.value}
        """
        await requests_channel.send(textwrap.dedent(request_string), view=RequestView(interaction.user, self.subject_input.value))
        await requests_channel.send("--------------------")

        await interaction.response.send_message('Your request has been submitted! You will be pinged when a mentor accepts it.', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        traceback.print_exception(type(error), error, error.__traceback__)


class Mentoring(commands.Cog):
    """Cog for mentor requests"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def setup_hook(self) -> None:
        self.bot.add_view(RequestView())

    @app_commands.command()
    async def request_mentor(self, interaction: discord.Interaction):
        """Opens a mentor request form"""

        request_modal = RequestModal()
        await interaction.response.send_modal(request_modal)


async def setup(bot):
    await bot.add_cog(Mentoring(bot))
