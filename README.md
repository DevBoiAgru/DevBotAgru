# DevBotAgru

A small discord bot with fun features.

## Commands list:

-   Help: /help
-   AI Chatbot: /devbot `prompt`
-   AI Image Generation: /imagen `prompt`
-   Dad joke: /dadjoke
-   Random joke: /joke
-   Fun fact: /fact
-   About the bot: /about
-   Check latency and connectivity: /ping

### Coming soon:

-   Moderation

## How to run

1. Clone the github repo:

```bash
git clone https://github.com/DevBoiAgru/DevBotAgru.git
```

2. Navigate into the repo

```bash
cd DevBotAgru
```

3. Duplicate `.env.example`, rename it to `.env` and put details in it
4. Set up a python virtual environment and activate it

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate.bat	# windows
source .venv/bin/activate 	# linux
```

5. Install dependencies

```bash
pip install -r requirements.txt
```

6. Run the bot

```bash
python bot.py
```

## Contributing

Contributions are welcome, everything from new features to bug reports etc is appreciated.
Create an issue for reporting a bug, and a pull request for a fix, or a new feature. You can always fork the project too
