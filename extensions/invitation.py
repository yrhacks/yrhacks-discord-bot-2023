import os
from dotenv import load_dotenv
from discord.ext import commands
import base64
from email.mime.text import MIMEText

load_dotenv()

# Constants
MESSAGE = """<html>
  <body>
    <p>Hi! Please click the link below to join the YRHacks Discord server.</p>

    <a href={link}>{link}</a>
  </body>
</html>"""
FROM = "yrhacks@gapps.yrdsb.ca"
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
        draft = self.bot.get_cog('APIs').create_draft(create_message)
        self.drafts.append(draft)

    def is_owner(self, ctx):
        """Check if the user is the owner"""
        return ctx.author.id == self.bot.owner_id

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_drafts(self, ctx):
        """Create drafts for all members"""

        values = self.bot.get_cog('APIs').get_spreadsheet_data(
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
