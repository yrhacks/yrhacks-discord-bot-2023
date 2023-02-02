from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()


class Invitation(commands.Cog):
    """Cog for generating one-time invitation links and emailing them"""

    def __init__(self, bot):
        self.bot = bot

    async def generate_invite_link(self, ctx):
        """Generate a one-time invite link"""
        channel = ctx.channel
        invite = await channel.create_invite(max_uses=1)
        return invite.url

    def create_draft(self, ctx, email_address):
        """Create a draft invitation link for a member"""
        pass

    @commands.command()
    async def create_drafts(self, ctx):
        """Create drafts for all members"""
        pass

    @commands.command()
    async def send_drafts(self, ctx):
        """Send all drafts to their respective members"""
        pass

    @commands.command()
    async def test(self, ctx):
        link = await self.generate_invite_link(ctx)
        print(link)


async def setup(bot):
    await bot.add_cog(Invitation(bot))
