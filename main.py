import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


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
