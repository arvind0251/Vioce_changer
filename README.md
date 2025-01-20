# Telegram Voice Changer Bot

This bot modifies voice messages by changing their pitch to sound like a female voice.

## Requirements

- Python 3.9 or higher
- Telegram Bot API Token
- ffmpeg installed on your system

## Setup

1. Clone the repository or unzip the files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your Telegram Bot API token to the `.env` file.
4. Run the bot:
   ```bash
   python bot.py
   ```

## Deploy on Heroku

1. Install Heroku CLI and log in:
   ```bash
   heroku login
   ```
2. Add buildpacks for ffmpeg:
   ```bash
   heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
   ```
3. Push to Heroku:
   ```bash
   git push heroku main
   ```
