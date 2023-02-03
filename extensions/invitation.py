import os
from dotenv import load_dotenv
from discord.ext import commands
import base64
from email.message import EmailMessage

load_dotenv()

# Constants
MESSAGE = """Hi! Please click the link below to join the YRHacks Discord server.

{link}"""
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
        message = EmailMessage()
        message.set_content(MESSAGE.format(link=link))

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

        draft = self.bot.get_cog('APIs').create_draft(create_message)
        self.drafts.append(draft)
        print(F'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

    @commands.command()
    async def create_drafts(self, ctx):
        """Create drafts for all members"""

        values = self.bot.get_cog('APIs').get_spreadsheet_data(
            os.getenv('SPREADSHEET_ID'), os.getenv('SPREADSHEET_EMAIL_RANGE'))
        emails = [value[0] for value in values]

        for email in emails:
            await self.create_draft(ctx, email)

    @commands.command()
    async def send_drafts(self, ctx):
        """Send all drafts to their respective members"""
        pass


async def setup(bot):
    await bot.add_cog(Invitation(bot))
