import os
import numpy as np
from pydub import AudioSegment
import sox  # Importing the sox library
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import Filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Set FFmpeg and SoX paths
AudioSegment.converter = os.getenv('FFMPEG_BINARY', '/app/.heroku/vendor/bin/ffmpeg')
AudioSegment.ffprobe = os.getenv('FFPROBE_BINARY', '/app/.heroku/vendor/bin/ffprobe')
os.environ["SOX_PATH"] = "/app/.heroku/vendor/bin/sox"

# Function to process voice and change pitch using SoX
def change_voice(input_file, output_file):
    # Create a SoX transformer
    tfm = sox.Transformer()
    
    # Apply pitch shift (use n_steps as desired for pitch shifting)
    tfm.pitch(5)  # Pitch shift by 5 semitones (adjust as necessary)

    # Perform the transformation and save the output
    tfm.build(input_file, output_file)

# Command to start the bot
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Mujhe apna voice message bhejiye, main usse ladki ki voice mein badal dunga!")

# Handle voice messages
def handle_voice(update: Update, context: CallbackContext):
    user = update.message.from_user
    voice_file = update.message.voice.get_file()
    input_path = f"{user.id}_input.ogg"
    output_path = f"{user.id}_output.ogg"

    # Download voice file
    voice_file.download(input_path)

    # Change voice pitch using SoX
    change_voice(input_path, output_path)

    # Send modified voice back
    with open(output_path, 'rb') as voice:
        update.message.reply_voice(voice)

    # Cleanup files
    os.remove(input_path)
    os.remove(output_path)

# Main function to run the bot
def main():
    try:
        print("Starting bot...")
        updater = Updater(API_TOKEN, use_context=True)

        # Check if token is valid
        if not API_TOKEN:
            raise ValueError("TELEGRAM_API_TOKEN is missing. Please check your environment variables.")

        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.voice, handle_voice))

        updater.start_polling()
        print("Bot is running...")
        updater.idle()
    except Exception as e:
        print(f"Error starting the bot: {e}")

if __name__ == "__main__":
    main()
