import discord
import aiohttp
from discord.ext import commands
from lib.utils.strings import shorten


class MessageUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="mentions",
        description="Find the last 5 messages mentioning you in this channel"
    )
    async def mentions(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.defer()

        # Search endpoint reference:
        # https://github.com/discord/discord-api-docs/blob/main/developers/resources/message.mdx#search-guild-messages
        url = (
            f"https://discord.com/api/v10/guilds/{ctx.guild.id}"
            "/messages/search"
        )

        params = {
            "mentions": str(ctx.author.id),
            "channel_id": str(ctx.channel.id),
            "sort_by": "timestamp",
            "sort_order": "desc",
            "offset": 0,
            "limit": 5,
        }

        headers = {
            "Authorization": f"Bot {self.bot.http.token}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, headers=headers
                ) as response:
                    if response.status != 200:
                        await ctx.interaction.followup.send(
                            "Error occured and couldn't search for your mentions.",
                            ephemeral=True
                        )
                        return

                    data = await response.json()

        except aiohttp.ClientError:
            await ctx.interaction.followup.send(
                "Something went wrong while searching for mentions.",
                ephemeral=True
            )
            return

        messages = [
            message
            for group in data.get("messages", [])
            for message in group
        ]

        if not messages:
            await ctx.interaction.followup.send(
                "No recent mentions found!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Your recent mentions in this channel",
            color=self.bot.bot_colour
        )

        for message in messages:
            # Show whether the message contains an embed
            content = (
                "*(Embed)*"
                if message.get("embeds")
                else shorten(message.get("content") or "(No content)", 150)
            )

            username = shorten(
                message.get("author", {}).get("username", "Unknown"),
                50
            )

            embed.add_field(
                name=f"{username} says: {content}"[:256],
                value=(
                    f"[Jump to message]"
                    f"(https://discord.com/channels/"
                    f"{ctx.guild.id}/{message['channel_id']}/"
                    f"{message['id']})"
                ),
                inline=False
            )

        await ctx.interaction.followup.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(MessageUtils(bot))
