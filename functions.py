import discord, os, json, requests, random, praw, datetime
from urllib.request import urlopen
from dotenv import load_dotenv

load_dotenv()

# Secrets
API_NINJA_KEY        = os.getenv("API_NINJA_KEY")                 # Used for Fun facts, dad jokes, and jokes
REDDIT_CLIENT_ID     = os.getenv("REDDIT_CLIENT_ID")              # Used for Python Reddit API Wrapper
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")          # Used for Python Reddit API Wrapper
REDDIT_USER_AGENT    = os.getenv("REDDIT_USER_AGENT")             # Used for Python Reddit API Wrapper
BOT_TOKEN            = os.getenv("BOT_TOKEN")                     # Discord Bot Token
DOPPLE_ID            = os.getenv("DOPPLE_ID")                     # Dopple ID
DOPPLE_CHAT_ID       = os.getenv("DOPPLE_CHAT_ID")                # Dopple chat ID
DOPPLE_USERNAME      = os.getenv("DOPPLE_USERNAME")               # Dopple registered username
DOPPLE_COOKIE        = os.getenv("DOPPLE_COOKIE")                 # Dopple cookie

# Customisable values:
LOG_TO_FILE        = False                        # Set to true if you want it to output logs to a file
embed_colour       = [8, 234, 142]                # R,G,B
error_embed_colour = [250, 0, 0]                  # R, G, B
memesubs = [                                      # Subreddits to get a meme from
    "memes",
    "dankmemes",
    "196",
    "surrealmemes"
]

# Initialise PRAW with account information, used for accessing reddit API.
reddit = praw.Reddit(client_id = REDDIT_CLIENT_ID,
                     client_secret = REDDIT_CLIENT_SECRET,
                     user_agent = REDDIT_USER_AGENT,
                     check_for_async = False)

# <-------ALL THE FUNCTIONS USED BY THE BOT------->

# Function to return an error embed with desired content
def error(title, description):
    erroremb = discord.Embed(title=title, description=description, colour=discord.Color.from_rgb(error_embed_colour[0], error_embed_colour[1], error_embed_colour[2]))
    return erroremb

# Function to log stuff, optionally to a text file
def log(text):
    logtext = "[" + str(datetime.datetime.now()) + "] " + text
    print (logtext)
    if LOG_TO_FILE:
        with open("exhaust.txt", "a", encoding="utf-8") as text_file:   # Exhaust.txt is the name of the log file
            text_file.write(logtext)

# Define a function to return ai output on a given input
def gpt(prmpt :str):
  print (f"[PROMPT]: {prmpt}")
  payload = {
    "streamMode": "none",
    "chatId": DOPPLE_CHAT_ID,
    "folder": "",
    "images": False,
    "username": DOPPLE_USERNAME,
    "id": DOPPLE_ID,
    "userQuery": prmpt
  }
  
  headers = {
    "Content-Type": "application/json",
    "Cookie": DOPPLE_COOKIE
  }

  response = requests.post("https://beta.dopple.ai/api/messages/send", json=payload, headers=headers)
  try:
    response_text = response.json()["response"]
    print (f"[AI]: {response_text}")
    return response_text
  except Exception as e:
    print (f"Error while getting AI response: {response.text}")
    print(e)
    return e

# Function to generate an AI generated image, FAST
def ImageGen(PROMPT):
    payload = {
        "prompt": PROMPT,
        "negative_prompt": "NSFW, (worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((grayscale)), skin spots, acnes, skin blemishes, age spot, (ugly:1.331), (duplicate:1.331), (morbid:1.21), (mutilated:1.21), (tranny:1.331), mutated hands, (poorly drawn hands:1.5), blurry, (bad anatomy:1.21), (bad proportions:1.331), extra limbs, (disfigured:1.331), (missing arms:1.331), (extra legs:1.331), (fused fingers:1.61051), (too many fingers:1.61051), (unclear eyes:1.331), lowers, bad hands, missing fingers, extra digit,bad hands, missing fingers, (((extra arms and legs)))",
        "source": "sdxlturbo.ai"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post("https://sd.cuilutech.com/sdapi/turbo/txt2img", json=payload, headers=headers, verify=False).json()
    if response["code"] == 200:
        log(f"[IMAGE GEN] PROMPT: {PROMPT}, RESULT: {response['data']['image_url']}")
        return (response["data"]["image_url"], 200)
    else:
        return ("https://cdn.discordapp.com/attachments/1172240777599004863/1188333969444442122/Error.png?ex=659a2540&is=6587b040&hm=5b881e51338f0ccaa8b6cb5798b3b4ecc6ef93c5c708257442cabb08e9d9fb7b&", response["code"])

# Function to make an embed with the best posts of a given subreddit
def meme(posts_lim):

    subreddit = random.choice(memesubs)

    # subreddit - What subreddit
    # posts_lim - How many top posts to choose from

    # Get some top posts from a subreddit to choose from
    submissions = list(reddit.subreddit(subreddit).hot(limit=posts_lim))

    # Get a random post from the chosen top posts and reroll if post is nsfw
    post = submissions[random.randrange(-1, posts_lim)]

    # Read the post JSON
    json_url = "https://www.reddit.com" + post.permalink + ".json"
    json_data = urlopen(json_url).read().decode('utf-8')
    post_json = json.loads(json_data)   
    # Get image or gif embed, if any.
    try:
      # Parse the json for the image link
      img_link = post_json[0]["data"]["children"][0]["data"]["url_overridden_by_dest"]
      img_extension = img_link[-5:] #Get last 5 characters of the link which contains the file's extension
    except KeyError as err:
      log("[REDDIT POST]: No media found, retrying...")
      return meme(subreddit, posts_lim) 
    if post.over_18:
        log ("[REDDIT POST]: NSFW Post, skipping")
        return meme(subreddit, posts_lim)
    else:
        if any(extension in img_extension for extension in ("png", "jpg",  "jpeg", "gif")):
            # Create embed with post title + subreddit name
            log ("[REDDIT POST]: Title: " + post.title + " on r/" + subreddit)
            embed = discord.Embed(title=post.title, description="on r/" + subreddit, color = discord.Color.from_rgb(embed_colour[0], embed_colour[1], embed_colour[2]))
            embed.set_image(url = img_link)
        else:
            log ("[REDDIT POST]: Media not in a suitable format, retrying...")
            return meme(subreddit, posts_lim)

    # Return the embed
    return embed

# Function to return an embed with cat pics
def meow():
    catresponse = requests.get("https://api.thecatapi.com/v1/images/search")
    catdata = catresponse.json()
    catimg = url=catdata[0]['url']
    catembed = discord.Embed(title="Meow 🐈", colour=discord.Color.from_rgb(embed_colour[0], embed_colour[1], embed_colour[2]))
    catembed.set_image(url=catimg)
    log ("[CAT IMAGE]: URL: " + url + '\n')
    return catembed

# Function to return an embed with dog pics
def woof():
    dogresponse = requests.get("https://random.dog/woof.json")
    dogdata = dogresponse.json()
    dogimg = dogdata['url']
    if any(extension in dogimg[-5:] for extension in ("png", "jpg",  "jpeg", "gif")):
        dogembed = discord.Embed(title="Woof 🐕", colour=discord.Color.from_rgb(embed_colour[0], embed_colour[1], embed_colour[2]))
        dogembed.set_image(url=dogimg)
        log ("[DOG IMAGE]: URL: " + dogimg + '\n')
    else:
        log ("[DOG IMAGE]: Returned media URL not in suitable format. Skipping... URL: " + dogimg + '\n')
        return woof()
    return dogembed

# Function to return an embed with a joke
def joke():
    api_url = 'https://api.api-ninjas.com/v1/jokes?limit=1'
    jokeresponse = requests.get(api_url, headers={'X-Api-Key': API_NINJA_KEY})
    if jokeresponse.status_code == requests.codes.ok:
        jokedata = jokeresponse.json()
        joke = jokedata[0]["joke"]
        jokeembed = discord.Embed(title="Joke 🤣", description=joke, colour=discord.Color.from_rgb(embed_colour[0], embed_colour[1], embed_colour[2]))
        log("[JOKE]: " + joke + '\n')
        return jokeembed
    else:
        jokeembed = discord.Embed(title="No joke 😔", description="Error getting joke, try again later", colour=discord.Color.from_rgb(error_embed_colour[0], error_embed_colour[1], error_embed_colour[2]))
        log ("[JOKE]: ERROR: " + jokeresponse.status_code + jokeresponse.text + '\n')
    return jokeembed

# Function to return an embed with a dad joke
def dadjoke():
    api_url = 'https://api.api-ninjas.com/v1/dadjokes?limit=1'
    dadresponse = requests.get(api_url, headers={'X-Api-Key': API_NINJA_KEY})
    if dadresponse.status_code == requests.codes.ok:
        daddata = dadresponse.json()
        dadjoke = daddata[0]["joke"]
        dadembed = discord.Embed(title="Dad joke 😁", description=dadjoke, colour=discord.Color.from_rgb(embed_colour[0], embed_colour[1], embed_colour[2]))
        log("[DAD JOKE]: " + dadjoke + '\n')
    else:
        dadembed = discord.Embed(title="No dad joke 😔", description="Error getting dad joke, try again later", colour=discord.Color.from_rgb(error_embed_colour[0], error_embed_colour[1], error_embed_colour[2]))
        log ("[DAD JOKE]: ERROR: " + dadresponse.status_code + dadresponse.text + '\n')
    return dadembed

# Function to return an embed with a fact
def fact():
    api_url = 'https://api.api-ninjas.com/v1/facts?limit=1'
    factresponse = requests.get(api_url, headers={'X-Api-Key': API_NINJA_KEY})
    if factresponse.status_code == requests.codes.ok:
        factdata = factresponse.json()
        fact = factdata[0]["fact"]
        factembed = discord.Embed(title="Fun fact! 🤯", description=fact, colour=discord.Color.from_rgb(embed_colour[0], embed_colour[1], embed_colour[2]))
        log ("[FACT: " + fact)
    else:
        factembed = discord.Embed(title="Not so fun fact", description="Error getting fun fact, try again later", colour=discord.Color.from_rgb(error_embed_colour[0], error_embed_colour[1], error_embed_colour[2]))
        log ("[FACT]: ERROR: " + factresponse.status_code + factresponse.text + '\n')
    return factembed
