import os
import discord
from discord.ext import commands
from discord.utils import get
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

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            self.requester: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await interaction.guild.create_text_channel(
            name=channel_name, category=mentoring_category, overwrites=overwrites)

        await channel.send(textwrap.dedent(f"""
        Hello, {self.requester.mention}! {interaction.user.mention} has accepted your request for help concerning {self.request_subject}!
        Please use this channel to discuss your questions and concerns.
        """))

        button.style = discord.ButtonStyle.grey
        button.disabled = True
        button.label = "Accepted"
        await interaction.response.edit_message(view=self)


class RequestModal(discord.ui.Modal, title="Mentor Request"):
    def __init__(self, bot):
        super().__init__(timeout=None, custom_id='request_modal')
        self.bot = bot

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
        view = RequestView(interaction.user, self.subject_input.value)
        message = await requests_channel.send(textwrap.dedent(request_string), view=view)
        await requests_channel.send("--------------------")

        # Make view persistent
        self.bot.add_view(view=view, message_id=message.id)

        await interaction.response.send_message('Your request has been submitted! You will be pinged when a mentor accepts it.', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        traceback.print_exception(type(error), error, error.__traceback__)


class Mentoring(commands.Cog):
    """Cog for mentor requests"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def request_mentor(self, interaction: discord.Interaction):
        """Opens a mentor request form"""

        request_modal = RequestModal(self.bot)
        await interaction.response.send_modal(request_modal)


async def setup(bot):
    await bot.add_cog(Mentoring(bot))
