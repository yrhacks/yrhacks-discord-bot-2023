import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from googleapiclient.errors import HttpError

load_dotenv()
discord.utils.setup_logging()

GUILD = discord.Object(id=int(os.getenv('GUILD_ID')))


class MyBot(commands.Bot):
    def __init__(self, *, command_prefix, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = MyBot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


async def load_extensions():
    for filename in os.listdir("./extensions"):
        if filename.endswith(".py"):
            await bot.load_extension(f"extensions.{filename[:-3]}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv('DISCORD_TOKEN'))

asyncio.run(main())
