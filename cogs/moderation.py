import discord
from discord.ext import commands
from lib.types import DCBot
from lib.calc import Calculator, InvalidExpression, InputTooLong, ResultTooBig, CalculatorError
import aiohttp
import time
import random

class Moderation(commands.Cog):
    def __init__(self, bot: DCBot):
        self.bot = bot

    @discord.slash_command(name="nick", description="Change someone's nickname")
    @commands.has_permissions(manage_nicknames=True)
    async def jew(
            self, 
            ctx: discord.ApplicationContext, 
            target: discord.Option(discord.Member, description="The member whose nickname you want to change"), # pyright: ignore[reportInvalidTypeForm], 
            newnick: discord.Option(str, description="The new nickname for the member") # pyright: ignore[reportInvalidTypeForm],
        ):
        await target.edit(nick=newnick)
        await ctx.respond(f"Changed {target.mention}'s name to {newnick}.")


def setup(bot: DCBot):  # this is called by Pycord to setup the cog
    bot.add_cog(Moderation(bot))  # add the cog to the bot
