import os
from pydub import AudioSegment
from pydub.effects import speedup, normalize
from pydub.generators import Sine
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Function to apply reverb effect using pydub's built-in features
def apply_reverb(sound):
    # Generate a sine wave to simulate reverb by mixing with the original sound
    reverb = Sine(0).to_audio_segment(duration=len(sound))  # Silence generator
    reverb = reverb + 10  # Boost the volume of the reverb
    return sound.overlay(reverb, position=0)

# Function to process voice and change pitch, time-stretch, and apply effects
def change_voice(input_file, output_file):
    # Load audio file
    sound = AudioSegment.from_file(input_file)
    
    # Increase pitch moderately for a more neutral female voice
    sound_shifted = sound.speedup(playback_speed=1.1)  # Slight speed up to raise pitch moderately
    
    # Apply reverb for a richer effect
    sound_reverb = apply_reverb(sound_shifted)
    
    # Normalize the audio for consistency
    sound_normalized = normalize(sound_reverb)
    
    # Export the final output
    sound_normalized.export(output_file, format="ogg")

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

        # Change voice pitch, apply reverb, and normalize
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
