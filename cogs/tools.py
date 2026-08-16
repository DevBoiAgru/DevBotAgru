import discord
from discord.ext import commands
from lib.types import DCBot
import requests


class Tools(commands.Cog):
    def __init__(self, bot: DCBot):
        self.bot = bot

    # Utility commands
    @discord.slash_command(name="currency", description="Convert amount between currencies using 3 letter codes like USD, EUR, INR")
    async def currency_convert(self, ctx: discord.ApplicationContext, amount: float, base: str, target: str):
        base = base.upper()
        target = target.upper()

        url = f"https://v6.exchangerate-api.com/v6/{self.bot.currency_apiKey}/pair/{base}/{target}/{amount}"

        req = requests.get(url)
        data = req.json()

        currEmbed = discord.Embed()

        if data.get("result") == "error":
            error = data.get("error-type", "unknown-error")

            errorMeanings = {
                "unsupported-code": "Currency is not supported.",
                "quota-reached": "Rate limited. Monthly quota for conversion reached.",
                "unknown-error": "Unknown error.",
            }

            currEmbed.color = self.bot.err_colour
            currEmbed.title = "Error while converting currencies!"
            currEmbed.add_field(
                name="Error",
                value=errorMeanings.get(error, "Unknown error."),
                inline=False,
            )

        else:
            currEmbed.color = self.bot.bot_colour
            currEmbed.title = "Currency Conversion"
            currEmbed.description = (
                f"{amount:g} {base} is **{data['conversion_result']:g} {target}**"
            )
            currEmbed.set_footer(
                text=f"Rate: 1 {base} = {data['conversion_rate']:g} {target}"
            )

        await ctx.respond(embed=currEmbed)



def setup(bot: DCBot):  # this is called by Pycord to setup the cog
    bot.add_cog(Tools(bot))  # add the cog to the bot
