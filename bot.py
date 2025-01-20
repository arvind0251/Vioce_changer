import os
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import lfilter
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Function to apply reverb effect
def apply_reverb(y, sr):
    # Simple reverb effect using an exponential decay
    decay = 0.5
    delay = int(0.1 * sr)  # 100 ms delay
    reverb = np.zeros(len(y) + delay)
    reverb[delay:] = y * decay
    return y + reverb[:len(y)]

# Function to process voice and change pitch and apply effects
def change_voice(input_file, output_file):
    # Load the audio file
    y, sr = librosa.load(input_file, sr=None)

    # Shift the pitch (increase by 4 half-steps for a female voice)
    y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=4)

    # Apply reverb effect
    y_reverb = apply_reverb(y_shifted, sr)

    # Save the modified audio
    sf.write(output_file, y_reverb, sr)

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

    # Change voice pitch and apply effects
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
        if not API_TOKEN:
            raise ValueError("TELEGRAM_API_TOKEN is missing. Please check your environment variables.")

        # Remove use_context=True
        updater = Updater(API_TOKEN)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(filters.Voice(), handle_voice))  # Use filters.Voice()

        updater.start_polling()
        print("Bot is running...")
        updater.idle()
    except Exception as e:
        print(f"Error starting the bot: {e}")

if __name__ == "__main__":
    main()
