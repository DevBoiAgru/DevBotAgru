import discord
from discord.ext import commands
from lib.types import DCBot
from lib.calc import Calculator, InvalidExpression, InputTooLong, ResultTooBig, CalculatorError
import aiohttp
import time


class Tools(commands.Cog):
    def __init__(self, bot: DCBot):
        self.bot = bot
        self.currency_rates = {}    # Cache for currency rates. Format: {(BASE, TARG): (RATE, EXPIRY)}, Example: {("USD", "EUR"): (0.85, 1786960000)} 

    async def __get_currency_rate(self, base: str, target: str):
        base = base.upper()
        target = target.upper()

        cache_key = (base, target)

        # Check cache
        if cache_key in self.currency_rates:
            rate, expiry = self.currency_rates[cache_key]

            if time.monotonic() < expiry:
                return {
                    "success": True,
                    "rate": rate,
                    "error": None,
                }

        # Not cached or cache expired
        url = (
            f"https://v6.exchangerate-api.com/v6/{self.bot.currency_apiKey}/pair/{base}/{target}"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

        if data.get("result") == "error":
            return {
                "success": False,
                "error": data.get("error-type", "unknown-error"),
                "rate": None,
            }

        rate = data["conversion_rate"]

        expiry = time.monotonic() + (60 * 60 * 48)

        # Cache BASE to TARGET as well as TARGET to BASE by reciprocating the rate
        self.currency_rates[(base, target)] = (rate, expiry)
        self.currency_rates[(target, base)] = (1 / rate, expiry)

        return {
            "success": True,
            "rate": rate,
            "error": None,
        }


    # Useful commands
    @discord.slash_command(
        name="currency",
        description="Convert amount between currencies using 3 letter codes like USD, EUR, INR"
    )
    async def currency_convert(
        self,
        ctx: discord.ApplicationContext,
        amount: discord.Option(float, description="How much currency to convert"), # pyright: ignore[reportInvalidTypeForm],
        base: discord.Option(str, description="The currency to convert from. Example: INR, USD (3 Letter code)"), # pyright: ignore[reportInvalidTypeForm]
        target: discord.Option(str, description="The currency to convert to. Example: USD, EUR (3 Letter code)") # pyright: ignore[reportInvalidTypeForm]
    ):
        base = base.upper()
        target = target.upper()

        data = await self.__get_currency_rate(base, target)

        currEmbed = discord.Embed()

        if not data["success"]:
            error = data["error"]

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
            rate = data["rate"]
            converted = amount * rate

            currEmbed.color = self.bot.bot_colour
            currEmbed.title = "Currency Conversion"
            currEmbed.description = (
                f"{amount:g} {base} is **{converted:g} {target}**"
            )
            currEmbed.set_footer(
                text=f"Rate: 1 {base} = {rate:g} {target}"
            )

        await ctx.respond(embed=currEmbed)


    @discord.slash_command(
        name="calc",
        description="Short for calculator. Solves expressions like 2+3/2*(10*10). Supports: +-*/^ and sqrt()"
    )
    async def calc(
        self,
        ctx: discord.ApplicationContext,
        expression: discord.Option(str, description="The mathematical expression to calculate. pi and e can be used as constants"), # pyright: ignore[reportInvalidTypeForm],
    ):
        calculator = Calculator()
        embed = discord.Embed()

        try:
            if len(expression) > 250:
                raise InputTooLong("Input expression too long")
            val = calculator.solve(expression)
            embed.title = expression
            embed.description = f"**{str(val)}**"
            embed.color = self.bot.bot_colour

        except CalculatorError as e:
            embed.title = "Calc Error"
            embed.color = self.bot.err_colour
            embed.description = str(e)

            if isinstance(e, InputTooLong):
                embed.title = "Input error"
            elif isinstance(e, InvalidExpression):
                embed.title = "Invalid expression"
            elif isinstance(e, ResultTooBig):
                embed.title = "Result too big to display"

        await ctx.respond(embed=embed)

def setup(bot: DCBot):  # this is called by Pycord to setup the cog
    bot.add_cog(Tools(bot))  # add the cog to the bot
