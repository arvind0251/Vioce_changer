import os
import logging
import tempfile
from pydub import AudioSegment, normalize
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import librosa
import soundfile as sf
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Function to apply pitch shift using librosa
def pitch_shift_librosa(input_file, output_file, n_steps=3):
    try:
        y, sr = librosa.load(input_file, sr=None)
        y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=n_steps)
        sf.write(output_file, y_shifted, sr)
        logging.info("Pitch shift applied successfully.")
    except Exception as e:
        logging.error(f"Error in pitch shifting: {e}")

# Function to apply reverb using FFmpeg
def apply_reverb_ffmpeg(input_file, output_file):
    try:
        cmd = [
            "ffmpeg", "-i", input_file,
            "-af", "aecho=0.8:0.88:60:0.4",
            output_file
        ]
        subprocess.run(cmd, check=True)
        logging.info("Reverb applied successfully using FFmpeg.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error applying reverb: {e}")

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mujhe apna voice message bhejiye, main usse ladki ki voice mein badal dunga!")

# Handle voice messages
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        voice_file = await update.message.voice.get_file()
        logging.info(f"Voice message received from user: {user.id}")

        # Use temporary files for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as input_temp, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as pitch_temp, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as output_temp:
            
            # Download voice file
            await voice_file.download_to_drive(input_temp.name)
            logging.info(f"Voice file downloaded: {input_temp.name}")

            # Apply pitch shift
            pitch_shift_librosa(input_temp.name, pitch_temp.name, n_steps=3)

            # Apply reverb
            apply_reverb_ffmpeg(pitch_temp.name, output_temp.name)

            # Send modified voice back
            with open(output_temp.name, 'rb') as voice:
                await update.message.reply_voice(voice)

        # Cleanup temporary files
        os.unlink(input_temp.name)
        os.unlink(pitch_temp.name)
        os.unlink(output_temp.name)
        logging.info("Temporary files deleted.")

    except Exception as e:
        logging.error(f"Error handling voice message: {e}")
        await update.message.reply_text("Kuch galat ho gaya hai. Kripya phir try karein!")

# Main function to run the bot
def main():
    try:
        logging.info("Starting bot...")
        if not API_TOKEN:
            raise ValueError("TELEGRAM_API_TOKEN is missing. Please check your environment variables.")

        # Use ApplicationBuilder instead of Updater
        application = ApplicationBuilder().token(API_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.VOICE, handle_voice))

        application.run_polling()
        logging.info("Bot is running...")
    except Exception as e:
        logging.error(f"Error starting the bot: {e}")

if __name__ == "__main__":
    main()
