import discord
import logging
import sys
import time
import os
from discord.ext import tasks
from dotenv import load_dotenv
from collections import deque
from itertools import cycle

load_dotenv()


class DCBot(discord.Bot):
    """Subclass to add configuration options"""

    def __init__(
        self,
        gemini_key: str | None,
        gemini_prompt: str | None,
        bot_colour: discord.Colour,
        start_time: int,
        ai_context_length: int,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.gemini_key: str | None = gemini_key
        self.gemini_prompt: str | None = gemini_prompt
        self.bot_colour: discord.Colour = bot_colour
        self.start_time: int = start_time
        self.ai_context: dict[
            int, deque[str]
        ] = {}  # A map of last few messages of chat with AI in a server.
        self.ai_context_length: int = ai_context_length


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
    gemini_key=os.getenv("GEMINI_KEY"),
    gemini_prompt=os.getenv("GEMINI_PROMPT"),
    bot_colour=discord.Colour.from_rgb(0, 0, 255),
    start_time=int(time.time()),
    ai_context_length=20,  # Number of queries given to AI to save as context (for each server)
)

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
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

    cycle_status.start()
    logging.info("[STATUS UPDATE] Started cycling through statusses")


bot.run(os.getenv("BOT_TOKEN"))
