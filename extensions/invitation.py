import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

# Constants
MESSAGE = """
Hi! Please click the link below to join the YRHacks Discord server.

{link}
"""
SUBJECT = "YRHacks Discord Server Invitation"


class Invitation(commands.Cog):
    """Cog for generating one-time invitation links and emailing them"""

    def __init__(self, bot):
        self.bot = bot
        self.drafts = []

    async def generate_invite_link(self, ctx):
        """Generate a one-time invite link"""
        channel = ctx.channel
        invite = await channel.create_invite(max_uses=1)
        return invite.url

    async def create_draft(self, ctx, email_address):
        """Create a draft invitation link for a member"""
        pass

    @commands.command()
    async def create_drafts(self, ctx):
        """Create drafts for all members"""

        if self.service == None:
            self.auth_google_api()

    @commands.command()
    async def send_drafts(self, ctx):
        """Send all drafts to their respective members"""
        pass

    @commands.command()
    async def test(self, ctx):
        self.create_drafts(ctx)


async def setup(bot):
    await bot.add_cog(Invitation(bot))
