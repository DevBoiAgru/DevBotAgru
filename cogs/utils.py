import discord
from discord.ext import commands
from lib.types import DCBot


class Utils(commands.Cog):
    def __init__(self, bot: DCBot):
        self.bot = bot

    # Utility commands
    @discord.slash_command(name="ping", description="Pong!")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(
            embed=discord.Embed(
                color=self.bot.bot_colour,
                title="Pong!",
                fields=[
                    discord.EmbedField(
                        name="Latency",
                        value=f"`{self.bot.latency:.2f} seconds`",
                        inline=True,
                    ),
                    discord.EmbedField(
                        name="Up since",
                        value=f"<t:{self.bot.start_time}:R>",
                        inline=True,
                    ),
                ],
            )
        )

    @discord.slash_command(name="about", description="Get details about the bot!")
    async def about(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(color=self.bot.bot_colour, title="About:")
        embed.description = (
            "A fun little bot made by @devboiagru for fun, with fun features."
        )
        embed.add_field(
            name="Source code:",
            value="https://github.com/DevBoiAgru/DevBotAgru/",
            inline=False,
        )
        embed.add_field(
            name="Up since:",
            value=f"<t:{self.bot.start_time}:R>",
            inline=False,
        )
        embed.set_author(
            name="DevBoiAgru",
            icon_url="https://cdn.discordapp.com/avatars/700572813009879170/59bdca68d5ec2a8a3b0292be4d1ab6cd",
        )
        embed.set_footer(
            text="Made with 💖 with Pycord", icon_url="https://i.imgur.com/FRpV6xv.png"
        )
        await ctx.respond(embed=embed)


def setup(bot: DCBot):  # this is called by Pycord to setup the cog
    bot.add_cog(Utils(bot))  # add the cog to the bot
