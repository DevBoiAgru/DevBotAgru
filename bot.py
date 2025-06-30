import discord
import logging
import sys
import time
import os
from discord.ext import tasks
from dotenv import load_dotenv
from lib.types import DCBot
from itertools import cycle

load_dotenv(override=True)


PLAYING_STATUS = "with fire"  # Text to display when the bot has playing status
WATCHING_STATUS = "the world burn."  # Text to display when the bot has watching status
LISTENING_STATUS = "the voices"  # Text to display when bot has listening status
STREAMING_STATUS = "DevBoi's Games"  # Text to display when bot has streaming status

status_cycle = cycle(
    (
        discord.Activity(type=discord.ActivityType.playing, name=PLAYING_STATUS),
        discord.Activity(type=discord.ActivityType.watching, name=WATCHING_STATUS),
        discord.Activity(type=discord.ActivityType.listening, name=LISTENING_STATUS),
        discord.Activity(type=discord.ActivityType.streaming, name=STREAMING_STATUS),
    )
)


# Cycle through statusses every 25 seconds
@tasks.loop(seconds=25)
async def cycle_status():
    await bot.change_presence(activity=next(status_cycle))


bot = DCBot(
    gemini_key=os.getenv("GEMINI_KEY"),  # Google gemini API key
    gemini_prompt=os.getenv("GEMINI_PROMPT"),  # System prompt for the LLM
    bot_colour=discord.Colour.from_rgb(0, 0, 255),  # Colour for embeds
    err_colour=discord.Colour.from_rgb(255, 0, 0),
    start_time=int(time.time()),  # Bot startup time
    ai_context_length=20,  # Number of queries given to AI to save as context (for each server)
)

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - [{levelname}] - {message}",
    style="{",
    datefmt="%d-%m-%Y %H:%M",
    handlers=[
        logging.FileHandler("bot.log", "a", "utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

# Load cogs
cogs_list = ["fun", "utils", "ai"]
for cog in cogs_list:
    bot.load_extension(f"cogs.{cog}")


@bot.event
async def on_ready():
    logging.info(f"{bot.user} is ready and online!")

    logging.info("Syncing commands")
    await bot.sync_commands()
    logging.info("Synced commands")

    cycle_status.start()
    logging.info("[STATUS UPDATE] Started cycling through statusses")


bot.run(os.getenv("BOT_TOKEN"))
