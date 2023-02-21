import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class RequestView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


class RequestModal(discord.ui.Modal, title="Mentor Request"):
    subject_input = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Brief subject of interest",
        required=True,
        placeholder="e.g. C++, React"
    )

    async def on_submit(self, interaction: discord.Interaction):
        pass

    async def on_error(self, interaction: discord.Interaction, error):
        pass


class Mentoring(commands.Cog):
    """Cog for mentor requests"""

    @commands.command()
    async def request_mentor(self, ctx):
        """Opens a request modal"""

        request_modal = RequestModal()
        await ctx.interaction.response.send_modal(request_modal)


async def setup(bot):
    await bot.add_cog(Mentoring(bot))
