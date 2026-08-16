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


PLAYING_STATUS = "Playing with fire"  # Text to display when the bot has playing status
WATCHING_STATUS = "Watching the world burn."  # Text to display when the bot has watching status
LISTENING_STATUS = "Listening to the voices"  # Text to display when bot has listening status
STREAMING_STATUS = "Playing DevBoi's Games"  # Text to display when bot has streaming status

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

# Load API Keys, so that we can skip cogs if the keys used are not available
GEMINI_KEY = os.getenv("GEMINI_KEY")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")

bot = DCBot(
    gemini_key = GEMINI_KEY,
    gemini_prompt = os.getenv("GEMINI_PROMPT"),  # System prompt for the LLM,
    currency_apiKey= CURRENCY_API_KEY,
    bot_colour = discord.Colour.from_rgb(0, 0, 255),  # Colour for embeds
    err_colour = discord.Colour.from_rgb(255, 0, 0),
    start_time = int(time.time()),  # Bot startup time
    ai_context_length = 20,  # Number of queries given to AI to save as context (for each server)
)

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - [{levelname}] - {message}",
    style="{",
    datefmt="%d-%m-%Y %H:%M",
    handlers=[
        logging.FileHandler("log.txt", "a", "utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

# Load cogs
cogs_list = ["fun", "utils", "ai", "tools"]
for cog in cogs_list:
    if (GEMINI_KEY is None and cog == "ai"):
        logging.info("[COGS] Skipping loading AI cog because of no Gemini API key.")
        continue
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
