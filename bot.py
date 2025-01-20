import os
import numpy as np
import librosa
import soundfile as sf
import pyrubberband as pyrb
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Function to apply reverb effect
def apply_reverb(y, sr):
    decay = 0.5
    delay = int(0.1 * sr)  # 100 ms delay
    reverb = np.zeros(len(y) + delay)
    reverb[delay:] = y * decay
    return y + reverb[:len(y)]

# Function to process voice and change pitch, time-stretch, and apply effects
def change_voice(input_file, output_file):
    # Load audio file
    y, sr = librosa.load(input_file, sr=None)
    
    # Shift pitch for a "girl-like" voice (8 semitones up)
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=8)
    
    # Apply time-stretch for smoother effect (rate 1.1)
    y_stretched = pyrb.time_stretch(y_shifted, sr, rate=1.1)
    
    # Add reverb for a richer effect
    y_reverb = apply_reverb(y_stretched, sr)
    
    # Save the processed file
    sf.write(output_file, y_reverb, sr)

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mujhe apna voice message bhejiye, main usse ladki ki voice mein badal dunga!")

# Handle voice messages
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        voice_file = await update.message.voice.get_file()  # Await the coroutine
        input_path = f"{user.id}_input.ogg"
        output_path = f"{user.id}_output.ogg"

        # Download voice file
        await voice_file.download_to_drive(input_path)
        print(f"Voice file downloaded: {input_path}")

        # Change voice pitch, apply time stretch, and apply effects
        change_voice(input_path, output_path)
        print(f"Voice processing complete. Output saved: {output_path}")

        # Send modified voice back
        with open(output_path, 'rb') as voice:
            await update.message.reply_voice(voice)

        # Cleanup files
        os.remove(input_path)
        os.remove(output_path)
        print("Temporary files deleted.")

    except Exception as e:
        print(f"Error handling voice message: {e}")
        await update.message.reply_text("Kuch galat ho gaya hai. Kripya phir try karein!")

# Main function to run the bot
def main():
    try:
        print("Starting bot...")
        if not API_TOKEN:
            raise ValueError("TELEGRAM_API_TOKEN is missing. Please check your environment variables.")

        # Use ApplicationBuilder instead of Updater
        application = ApplicationBuilder().token(API_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.VOICE, handle_voice))  # Use filters.VOICE

        application.run_polling()
        print("Bot is running...")
    except Exception as e:
        print(f"Error starting the bot: {e}")

if __name__ == "__main__":
    main()
