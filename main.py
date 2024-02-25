# Stupid idiot bot
# Made by DevBoiAgru

import discord, traceback
import functions as f
from discord import app_commands
from discord.ext import commands, tasks
from itertools import cycle

# Initialize bot
TOKEN = f.BOT_TOKEN
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# Text to show when someone uses the help command
helptxt="""
# You have reached the help desk!

**Here are the commands you can use:** 

Help: /help
AI Chatbot: /devbot `your prompt`
AI Image generation: /imagen `your prompt`
Cat photo: /meow
Dog photo: /woof
Dad joke: /dadjoke
Random joke: /joke
Hot meme: /meme
Fun fact: /fact

**Moderation:**
Ban user: /ban `user` `reason`
Unban user: /unban `user id` `reason`
Kick user: /kick `user` `reason`
Timeout user: /timeout `user` `reason` `duration (days, hours, minutes, seconds)`
Delete recent messages: /purge `number`

**Enjoy!**
"""

PLAYING_STATUS   = "DevBoi's Games"                                             # Text to display when the bot has playing status
WATCHING_STATUS  = "the world burn."                                            # Text to display when the bot has watching status
LISTENING_STATUS = "the voices"                                                 # Text to display when bot has listening status
STREAMING_STATUS = "with fire"                                                  # Text to display when bot has streaming status
STREAM_URL       = "https://www.youtube.com/channel/UCUvotYmBARsxDRcyF2TvegA"   # Url to show when streaming status is applied

status_cycle = cycle((
   discord.Activity(type=discord.ActivityType.playing, name=PLAYING_STATUS),
   discord.Activity(type=discord.ActivityType.watching, name=WATCHING_STATUS),
   discord.Activity(type=discord.ActivityType.listening, name=LISTENING_STATUS),
   discord.Activity(type=discord.ActivityType.streaming, name=STREAMING_STATUS, url=STREAM_URL)
))

@bot.event
# BOT LOGIC
async def on_ready():
    f.log ("---BOT READY---" + '\n')
    cycle_status.start()
    f.log("[STATUS UPDATE] Started cycling through statusses")
    try:
        synced = await bot.tree.sync()
        f.log (f"[SYNC]: Synced {len(synced)} command(s) successfully!" '\n')
    except Exception as e:
        f.log("[SYNC]: ERROR: " + str(e))

# Cycle through statusses
@tasks.loop(seconds=25)
async def cycle_status():
    await bot.change_presence(activity=next(status_cycle))

# Event whenever a message is sent which the bot can read.
@bot.event
async def on_message(message):
    # Don't reply to itself
    if message.author.id == bot.user.id:
       pass
    
# <------- COMMANDS ------->
  # Check functions.py for the functions
  # Change the name and description of commands according to your liking


# Permissions and command error handling
@bot.tree.error
async def on_command_error(interaction :discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        msgembed = discord.Embed(title="Missing permissions", description= "Looks like you don't have the required permissions to use that command!",colour=discord.Color.from_rgb(f.error_embed_colour[0], f.error_embed_colour[1], f.error_embed_colour[2]))
        await interaction.followup.send(embed=msgembed, ephemeral=True)
        return
    if isinstance(error, app_commands.errors.MissingRole):
        msgembed = discord.Embed(title="Missing roles", description= "Looks like you don't have the required roles to use that command!",colour=discord.Color.from_rgb(f.error_embed_colour[0], f.error_embed_colour[1], f.error_embed_colour[2]))
        await interaction.followup.send(embed=msgembed, ephemeral=True)
        return
    if isinstance(error, app_commands.errors.BotMissingPermissions):
        msgembed = discord.Embed(title="Missing permissions", description= "Looks like I don't have the permissions to use that command!",colour=discord.Color.from_rgb(f.error_embed_colour[0], f.error_embed_colour[1], f.error_embed_colour[2]))
        await interaction.followup.send(embed=msgembed, ephemeral=True)
        return
    if isinstance(error, app_commands.errors.CommandOnCooldown):
        msgembed = discord.Embed(title="Hold on!", description= f"Command is on cooldown! Try again after {round(error.retry_after, 2)} seconds.",colour=discord.Color.from_rgb(f.error_embed_colour[0], f.error_embed_colour[1], f.error_embed_colour[2]))
        await interaction.followup.send(embed=msgembed, ephemeral=True)
        return
    if isinstance(error, app_commands.errors.CommandInvokeError):
        msgembed = discord.Embed(title="Command Error!", description= f"Error happened: {error}",colour=discord.Color.from_rgb(f.error_embed_colour[0], f.error_embed_colour[1], f.error_embed_colour[2]))
        await interaction.followup.send(embed=msgembed, ephemeral=True)
        return
    f.log(f"[COMMAND ERROR] Error {error} of type {type(error)}")


# Help
@app_commands.checks.cooldown(rate=1,per=5)
@bot.tree.command(name="help", description="Shows all the available commands")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  helpembed = discord.Embed(title="Looking for help? I got you 😉", description= helptxt, colour=discord.Color.from_rgb(f.embed_colour[0], f.embed_colour[1], f.embed_colour[2]))
  await interaction.followup.send(embed = helpembed, ephemeral=True)

# AI Chatbot
@app_commands.checks.cooldown(rate=1,per=5)
@bot.tree.command(name="devbot", description="Chat with DevBotAgru!")
@app_commands.describe(prompt = "Prompt")
async def ai(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    if len(prompt) > 255: # Check if prompt is too long
       msgembed = f.error("Prompt too long!", "Write a prompt shorter than 256 characters please 😁")
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
@app_commands.checks.cooldown(rate=1,per=5)
@bot.tree.command(name="fact", description="Get a random fun fact")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.fact(), ephemeral=False)

# Joke
@app_commands.checks.cooldown(rate=1,per=5)
@bot.tree.command(name="joke", description="Get a random joke")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.joke(), ephemeral=False)

# Dad joke
@app_commands.checks.cooldown(rate=1,per=5)
@bot.tree.command(name="dadjoke", description="Get a random dad joke")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.dadjoke(), ephemeral=False)

# Meme
@app_commands.checks.cooldown(rate=1,per=5)
@bot.tree.command(name="meme", description="Get a random meme from reddit")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.meme(10), ephemeral=False) 

# Cat pic
@app_commands.checks.cooldown(rate=1,per=5)
@bot.tree.command(name="meow", description="Get a random cat picture/gif")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.meow(), ephemeral=False)

# Dog pic
@app_commands.checks.cooldown(rate=1,per=5)
@bot.tree.command(name="woof", description="Get a random dog picture/gif")
async def help(interaction: discord.Interaction):
  await interaction.response.defer()
  await interaction.followup.send(embed = f.woof(), ephemeral=False)

# Image generator
@app_commands.checks.cooldown(rate=1,per=5)
@bot.tree.command(name="imagen", description="Generate images from text!")
@app_commands.describe(prompt = "Prompt")
async def img(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    if len(prompt) > 255: # Check if prompt is too long
       msgembed = f.error("Prompt too long!", "Write a prompt shorter than 256 characters please 😊")
    else: 
        result=f.ImageGen(prompt)
        msgembed = discord.Embed(title=prompt[:250],colour=discord.Color.from_rgb(f.embed_colour[0], f.embed_colour[1], f.embed_colour[2]))
        msgembed.set_image(url=result[0])

    await interaction.followup.send(embed = msgembed, ephemeral=False)

# <----------------- MODERATION COMMANDS ----------------->

# Purge
@bot.tree.command(name="purge", description="Delete 'n' most recent messages")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(num = "Number")
async def purge(interaction: discord.Interaction, num: int):
    await interaction.response.defer()
    await interaction.channel.purge(limit=(num+1))
    f.log(f"[PURGE]: Deleted {num} messages")

# Kick
@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.describe(member = "Member", reason = "Reason")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
    await interaction.response.defer()
    await member.kick(reason=reason)
    f.log(f"[KICK]: Kicked {member}")
    msgembed = discord.Embed(title=f"Kicked {member}", description= f"Reason: {reason}",colour=discord.Color.from_rgb(f.embed_colour[0], f.embed_colour[1], f.embed_colour[2]))
    await interaction.followup.send(embed=msgembed)

# Ban
@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(member = "Member", reason = "Reason")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
    await interaction.response.defer()  
    await member.ban(reason=reason, delete_message_seconds=603800)
    f.log(f"[BAN]: Banned {member}")
    msgembed = discord.Embed(title=f"Banned {member}", description= f"Reason: {reason}",colour=discord.Color.from_rgb(f.embed_colour[0], f.embed_colour[1], f.embed_colour[2]))
    await interaction.followup.send(embed=msgembed)

# Unban
@bot.tree.command(name="unban", description="Unban a member")
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(memberid = "User ID", reason= "Reason")
async def unban(interaction: discord.Interaction, memberid: str, reason: str = "None"):
    await interaction.response.defer()
    try:
        memberid = int(memberid)
        target = await bot.fetch_user(memberid)
        await interaction.guild.unban(target, reason=reason)
        f.log(f"[UNBAN]: Unbanned {target}")
        msgembed = discord.Embed(title=f"Unbanned {target}", description= f"Reason: {reason}",colour=discord.Color.from_rgb(f.embed_colour[0], f.embed_colour[1], f.embed_colour[2]))
    except ValueError:
        msgembed = discord.Embed(title="Invalid ID inputted", description= "Required ID is not a valid integer",colour=discord.Color.from_rgb(f.error_embed_colour[0], f.error_embed_colour[1], f.error_embed_colour[2]))
    except discord.NotFound:
        msgembed = discord.Embed(title="Member not found", description= "Member does not exist!",colour=discord.Color.from_rgb(f.error_embed_colour[0], f.error_embed_colour[1], f.error_embed_colour[2]))
    await interaction.followup.send(embed=msgembed)

# Timeout
@bot.tree.command(name="timeout", description="Timeout a member")
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.describe(member = "Member", reason = "Reason", days = "Days", hours = "Hours", minutes="Minutes", seconds="Seconds")
async def timeout(interaction: discord.Interaction, member: discord.Member, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, reason: str = None):
    await interaction.response.defer()
    duration = f.datetime.timedelta(seconds=seconds, minutes=minutes, hours= hours, days=0 if not any((seconds, minutes, hours, days)) else 1)
    await member.timeout(duration, reason=reason)
    msgembed = discord.Embed(title=f"Timed out {member}", description= f"For: {duration}\nReason: {reason}",colour=discord.Color.from_rgb(f.embed_colour[0], f.embed_colour[1], f.embed_colour[2]))
    await interaction.followup.send(embed=msgembed, ephemeral=False)

# Run the bot
bot.run(TOKEN)