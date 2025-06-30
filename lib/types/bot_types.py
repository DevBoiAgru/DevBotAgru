import discord
from collections import deque
from dataclasses import dataclass


@dataclass
class AIMessage:
    """A structure saving the message content, and if the message was sent by the bot or not."""

    isBot: bool
    message: str


class DCBot(discord.Bot):
    """A Discord bot subclass to add some more attributes useful for configuration and passing in values to cogs"""

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
        self.start_time: int = start_time

        self.bot_colour: discord.Colour = bot_colour
        self.err_colour: discord.Colour = bot_colour

        # A map of last few messages of chat with AI in a server. (guild_id : [list of messages in format {bot: bool, message: str}])
        self.ai_context: dict[int, deque[AIMessage]] = {}
        self.ai_context_length: int = ai_context_length
