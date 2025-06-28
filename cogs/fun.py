import discord
import json
import random
from discord.ext import commands


class Fun(commands.Cog):
    dadjokes: list[dict[str, str]]
    jokes: list[dict[str, str]]
    facts: list[dict[str, str]]

    def __init__(self, bot):
        self.bot = bot

        # Load jokes into memory
        with (
            open("assets/dadjokes.json") as a,
            open("assets/jokes.json") as b,
            open("assets/facts.json") as c,
        ):
            self.dadjokes = json.load(a)
            self.jokes = json.load(b)
            self.facts = json.load(c)

    def embed_structure(self):
        """Get an embed with some preset configuration"""
        return discord.Embed(color=self.bot.bot_colour)

    @discord.slash_command(name="dadjoke", description="Get a random dad joke")
    async def dad_joke(self, ctx: discord.ApplicationContext):
        dadjoke = random.choice(self.dadjokes)
        embed = self.embed_structure()
        embed.title = "Dadjoke!"
        embed.add_field(
            name=dadjoke.get("setup", "Couldn't fetch joke"),
            value=f"|| {dadjoke.get('punchline', 'Very unfortunate')} ||",
        )
        await ctx.respond(embed=embed)

    @discord.slash_command(name="joke", description="Get a random joke")
    async def joke(self, ctx: discord.ApplicationContext):
        rand_joke = random.choice(self.jokes)
        embed = self.embed_structure()
        embed.title = "Joke!"
        embed.add_field(
            name=rand_joke.get("setup", "Couldn't fetch joke"),
            value=f"|| {rand_joke.get('punchline', 'Very unfortunate')} ||",
        )
        await ctx.respond(embed=embed)

    @discord.slash_command(name="fact", description="Get a random fun fact")
    async def fact(self, ctx: discord.ApplicationContext):
        embed = self.embed_structure()
        embed.title = "Fun fact!"
        embed.description = random.choice(self.facts)
        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Fun(bot))  # add the cog to the bot
