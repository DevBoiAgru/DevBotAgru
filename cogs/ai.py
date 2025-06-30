import discord
import logging
import requests
import io
from datetime import datetime, timezone
from discord.ext import commands
from google import genai
from google.genai import types as genai_types
from collections import deque
from lib.types import DCBot, AIMessage

log = logging.getLogger(__name__)


class AI(commands.Cog):
    def __init__(self, bot: DCBot):
        self.bot = bot
        if self.bot.gemini_key:
            self.key_supplied = True
        else:
            self.key_supplied = False

        if self.key_supplied:
            self.genai_client = genai.Client(api_key=self.bot.gemini_key)

    @discord.slash_command(name="devbot", description="Chat with devbot!")
    async def devbot(self, ctx: discord.ApplicationContext, prompt: str):
        log.info(f"[AI CHATBOT]: User: {ctx.author.id} Prompt: {prompt}")

        if not self.key_supplied:
            log.warning(
                "[AI CHATBOT]: No gemini key provided, so /devbot command will lead to an error response."
            )
            await ctx.respond(
                embed=discord.Embed(
                    title="No gemini API key provided!",
                    description="If you are the developer of this bot provide a gemini AI key to use chatbot.",
                    color=self.bot.err_colour,
                )
            )
            return

        guild_id: int = ctx.interaction.guild_id if ctx.interaction.guild_id else -1

        if guild_id == -1:
            log.error("[AI CHATBOT]: Could not fetch guild id.")
            await ctx.respond(
                embed=discord.Embed(
                    title="Failed getting guild id.",
                    description="Could not figure out what server I am in. Perhaps this is not a guild?",
                    color=self.bot.err_colour,
                )
            )
            return

        server_context: deque | None = self.bot.ai_context.get(guild_id)

        if len(prompt) > 250:
            log.warning("[AI CHATBOT]: User prompt too long, not continuing.")
            await ctx.respond(
                embed=discord.Embed(
                    title="Prompt too long!",
                    description="Use a prompt less than 250 characters.",
                    color=self.bot.err_colour,
                )
            )
            return

        # Defer the interaction because generating the response can take longer than 3 seconds
        await ctx.interaction.response.defer()

        # If we dont have a history for this message, create a deque for it
        if not server_context:
            self.bot.ai_context[guild_id] = deque(
                maxlen=2 * self.bot.ai_context_length + 1
            )  # +1 for the system prompt, *2 since each message has a reply from the bot

        # Add prompt to history
        self.bot.ai_context[guild_id].append(
            AIMessage(False, f"{ctx.author.display_name} : {prompt}")
        )

        # Create a list of messages to send to gemini
        ai_context_messages = [
            genai_types.Content(
                role="user",
                parts=[
                    genai_types.Part.from_text(
                        text=f"{self.bot.gemini_prompt} In case you need this info, it is currently {datetime.now(timezone.utc).strftime('%Y/%m/%d %H:%M UTC')}"
                    )
                ],
            ),
        ]

        # Loop over all messages in the context for this particular guild and add them to the gemini context list
        # We do not need to check for the size since the ai_context is already a deque of a fixed size
        for msg in self.bot.ai_context[guild_id]:
            ai_context_messages.append(
                genai_types.Content(
                    role="model" if msg.isBot else "user",
                    parts=[genai_types.Part.from_text(text=msg.message)],
                ),
            )

        # Generate the message
        try:
            log.info(
                f"[AI CHATBOT]: Generating response using history for guild {ctx.interaction.guild_id}"
            )
            ai_reply = self.genai_client.models.generate_content(
                model="gemini-1.5-flash", contents=ai_context_messages
            ).text

            if not ai_reply:
                raise RuntimeError("Got an empty response from the AI!")

        except Exception:
            log.error("[AI CHATBOT]: Error while generating AI response", exc_info=True)
            await ctx.interaction.followup.send(
                embed=discord.Embed(
                    title="Error while generating response!",
                    description="An error occured while generating a response.",
                    color=self.bot.err_colour,
                )
            )
            return

        # Add ai reply to history
        self.bot.ai_context[guild_id].append(AIMessage(True, ai_reply))

        log.info(f"[AI CHATBOT]: Response: {ai_reply}")
        await ctx.interaction.followup.send(
            embed=discord.Embed(
                title=prompt, description=ai_reply, colour=self.bot.bot_colour
            )
        )

    @discord.slash_command(
        name="imagen", description="Generate images with AI using text!"
    )
    async def images(self, ctx: discord.ApplicationContext, prompt: str):
        logging.info(f"[IMAGE GEN]: User: {ctx.author.id} Prompt: {prompt}")

        if len(prompt) > 250:
            log.warning("[IMAGE GEN]: User prompt too long, not continuing.")
            await ctx.respond(
                embed=discord.Embed(
                    title="Prompt too long!",
                    description="Use a prompt less than 250 characters.",
                    color=self.bot.err_colour,
                )
            )
            return

        await ctx.interaction.response.defer()
        payload = f'-----011000010111000001101001\r\nContent-Disposition: form-data; name="prompt"\r\n\r\n{prompt}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="output_format"\r\n\r\nbytes\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="user_is_subscribed"\r\n\r\ntrue\r\n-----011000010111000001101001--\r\n'

        headers = headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "multipart/form-data; boundary=---011000010111000001101001",
            "origin": "https://magicstudio.com",
            "referer": "https://magicstudio.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

        response = requests.post(
            "https://ai-api.magicstudio.com/api/ai-art-generator",
            data=payload,
            headers=headers,
        )
        if response.status_code != 200:
            logging.error(
                f"[IMAGE GEN]: API Did not return 200. Status code: {response.status_code}"
            )
            logging.error(f"[IMAGE GEN]: Response: {response.text}")

            await ctx.interaction.followup.send(
                embed=discord.Embed(
                    title="Error while generating image!",
                    description=f"An error occured while generating a response. Status code: {response.status_code}",
                    color=self.bot.err_colour,
                )
            )
            return

        image: bytes = response.content

        if not image:
            logging.error(
                f"[IMAGE GEN]: No image found after generating: length: {len(image)}"
            )
            await ctx.interaction.followup.send(
                embed=discord.Embed(
                    title="Something went wrong while generating image!",
                    description="An error occured while generating a response. Couldn't generate image",
                    color=self.bot.err_colour,
                )
            )
            return

        logging.info(f"[IMAGE GEN]: Generated image. Prompt: {prompt}")
        with io.BytesIO() as image_binary:
            image_binary.write(image)
            image_binary.seek(0)
            await ctx.interaction.followup.send(
                content=prompt,
                file=discord.file.File(
                    fp=image_binary, filename="ai_generated_slop.png"
                ),
                ephemeral=False,
            )


def setup(bot: DCBot):  # this is called by Pycord to setup the cog
    bot.add_cog(AI(bot))  # add the cog to the bot
