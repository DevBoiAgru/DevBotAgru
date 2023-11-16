# Stupid idiot bot
# Made by DevBoiAgru

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import functions as f


# Initialize bot
TOKEN = f.BOT_TOKEN
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# CUSTOMIZABLE VARIABLES



# Text to show when someone uses the help command
helptxt="""
# You have reached the help desk!

**Here are the commands you can use:** 

Help: command syntax: /help
AI reply: command syntax: /devbot `your prompt`
Cat photos: /meow
Dog photos: /woof
Dad joke: /dadjoke
Joke: /joke
Meme: /meme
Fun fact: /fact

**Enjoy!**
"""

PLAYING_STATUS   = "DevBoi's Games"                                             # Text to display when the bot has playing status
WATCHING_STATUS  = "the world burn."                                            # Text to display when the bot has watching status
LISTENING_STATUS = "the voices"                                                 # Text to display when bot has listening status
STREAMING_STATUS = "with fire"                                                  # Text to display when bot has streaming status
STREAM_URL       = "https://www.youtube.com/channel/UCUvotYmBARsxDRcyF2TvegA"   # Url to show when streaming status is applied


@bot.event
# BOT LOGIC
async def on_ready():
    f.log ("---BOT READY---" + '\n')
    try:
        synced = await bot.tree.sync()
        f.log (f"[SYNC]: Synced {len(synced)} command(s) successfully!" '\n')
    except Exception as e:
        f.log("[SYNC]: ERROR: " + e)
    statusType = 0
    while True:
        # Cycle through status
        if statusType == 0:
            await bot.change_presence(activity=discord.Game(name=PLAYING_STATUS))
            print ("[STATUS UPDATED]: Changed status to playing." + '\n')
            statusType = 1
        elif statusType == 1:
            await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=WATCHING_STATUS))
            print ("[STATUS UPDATED]: Changed status to watching." + '\n')
            statusType = 2
        elif statusType == 2:
            await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=LISTENING_STATUS))
            print ("[STATUS UPDATED]: Changed status to listening." + '\n')
            statusType = 3
        else:
            await bot.change_presence(activity=discord.Streaming(name=STREAMING_STATUS, url=STREAM_URL))  
            print ("[STATUS UPDATED]: Changed status to streaming." + '\n')
            statusType = 0
        await asyncio.sleep(30) # Delay before switching to the next status

# Event whenever a message is sent which the bot can read.
@bot.event
async def on_message(message):
    # Don't reply to itself
    if message.author.id == bot.user.id:
       pass
    
# <------- COMMANDS ------->
  # Check functions.py for the functions
  # Change the name and description of commands according to your liking

# Command on cooldown
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        errembed = f.error("Command on cooldown.", "Slow down and try again later 😁")
        await ctx.send(embed = errembed)

# Help
@bot.tree.command(name="help", description="Shows all the available commands")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  helpembed = discord.Embed(title="Looking for help? I got you 😉", description= helptxt, colour=discord.Color.from_rgb(f.embed_colour[0], f.embed_colour[1], f.embed_colour[2]))
  await interaction.followup.send(embed = helpembed, ephemeral=True)

# AI Chatbot
@bot.tree.command(name="devbot", description="Chat with DevBotAgru!")
@app_commands.describe(prompt = "Prompt: ")
@commands.cooldown(1, 10, commands.BucketType.user)
async def ai(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    if len(prompt) > 255: # Check if prompt is too long
       msgembed = f.error("Prompt too long!", "Write a prompt shorter than 256 characters please 😊")
       f.log ("[AI]: Prompt too long: " + prompt)
    else: 
        result=f.gpt(prompt)
        if len(result) > 3999: # If message is huge then slice it into 2 parts and send them seperately
            msgembed = discord.Embed(title=prompt,description=result[:4000],colour=discord.Color.from_rgb(f.embed_colour[0], f.embed_colour[1], f.embed_colour[2]))
            await interaction.followup.send(embed = msgembed, ephemeral=False)
            msgembed = discord.Embed(title="continuing...",description=result[4000:],colour=discord.Color.from_rgb(f.embed_colour[0], f.embed_colour[1], f.embed_colour[2]))
            msgembed.add_field(name="Reply length: ", value=str(str(len(result)) + " characters."), inline=False)
            await interaction.followup.send(embed = msgembed, ephemeral=False)
        else: # If message is not very large, send it normally.
            # Use embed for replying
            msgembed = discord.Embed(title=prompt,description=result,colour=discord.Color.from_rgb(f.embed_colour[0], f.embed_colour[1], f.embed_colour[2]))
            msgembed.add_field(name="Reply length: ", value=str(str(len(result)) + " characters."), inline=False)
    await interaction.followup.send(embed = msgembed, ephemeral=False)

# Fact
@bot.tree.command(name="fact", description="Get a random fun fact")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.fact(), ephemeral=False)


# Joke
@bot.tree.command(name="joke", description="Get a random joke")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.joke(), ephemeral=False)

# Dad joke
@bot.tree.command(name="dadjoke", description="Get a random dad joke")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.dadjoke(), ephemeral=False)

# Meme
@bot.tree.command(name="meme", description="Get a random meme from reddit")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.meme(10), ephemeral=False) 

# Cat pic
@bot.tree.command(name="meow", description="Get a random cat picture/gif")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.meow(), ephemeral=False)

# Dog pic
@bot.tree.command(name="woof", description="Get a random dog picture/gif")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.woof(), ephemeral=False)




# Run the bot
bot.run(TOKEN)
