import os
import numpy as np
from pydub import AudioSegment
from pyrubberband import pyrb
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import Filters
from dotenv import load_dotenv

# Set ffmpeg and ffprobe path
AudioSegment.converter = os.getenv('FFMPEG_BINARY', 'ffmpeg')
AudioSegment.ffprobe = os.getenv('FFPROBE_BINARY', 'ffprobe')

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Set Rubberband path
os.environ["RUBBERBAND_PATH"] = "/app/.heroku/vendor/bin/rubberband"

# Function to process voice and change pitch
def change_voice(input_file, output_file):
    sound = AudioSegment.from_file(input_file, format="ogg")
    samples = np.array(sound.get_array_of_samples()).astype(np.float32) / (2**15)  # Normalize samples
    sample_rate = sound.frame_rate

    # Adjust pitch using Rubberband
    pitch_shifted = pyrb.pitch_shift(samples, sample_rate, n_steps=5)  # Adjust `n_steps` as needed

    # Convert back to AudioSegment
    pitch_shifted = (pitch_shifted * (2**15)).astype(np.int16)  # De-normalize samples
    new_sound = AudioSegment(
        pitch_shifted.tobytes(),
        frame_rate=sample_rate,
        sample_width=sound.sample_width,
        channels=sound.channels
    )

    # Export the processed file
    new_sound.export(output_file, format="ogg")

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

    # Change voice pitch
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
