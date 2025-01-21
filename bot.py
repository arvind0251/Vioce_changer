import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
from pydub import AudioSegment
from dotenv import load_dotenv
from voice_cloning.generation import speech_generator, save_sound  # Import the necessary functions

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Ensure API token is available before initializing the bot
if not API_TOKEN:
    raise ValueError("TELEGRAM_API_TOKEN is missing. Please check your .env file.")

# Define a temporary directory for file storage
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Function to process voice and change voice using voice cloning
async def change_voice(input_file: str, output_file: str):
    try:
        reference_voice_path = "path/to/your/reference_female_voice.wav"  # Update this path
        speech_text = "Your transformed voice message"

        # Generate the cloned voice
        generated_wav = await asyncio.to_thread(
            speech_generator,
            voice_type="western",
            sound_path=reference_voice_path,
            speech_text=speech_text
        )

        # Save the generated voice to the output file
        await asyncio.to_thread(save_sound, generated_wav, filename=output_file, noise_reduction=True)

    except Exception as e:
        print(f"Error in voice processing: {e}")
        return None

# Command to start the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Mujhe apna voice message bhejiye, main usse ladki ki voice mein badal dunga!")

# Handle voice messages
async def handle_voice(update: Update, context: CallbackContext):
    user = update.message.from_user
    voice_file = await update.message.voice.get_file()
    
    input_path = os.path.join(TEMP_DIR, f"{user.id}_input.ogg")
    output_path = os.path.join(TEMP_DIR, f"{user.id}_output.wav")

    # Download the voice file
    await voice_file.download_to_drive(input_path)

    # Convert OGG to WAV (if required)
    audio = AudioSegment.from_file(input_path, format="ogg")
    audio.export(input_path.replace(".ogg", ".wav"), format="wav")

    # Change voice using voice cloning
    result = await change_voice(input_path.replace(".ogg", ".wav"), output_path)

    if result is None:
        await update.message.reply_text("Maaf kijiye, voice cloning mein koi samasya aayi hai.")
        return

    # Send modified voice back
    with open(output_path, 'rb') as voice:
        await update.message.reply_voice(voice)

    # Cleanup files
    os.remove(input_path)
    os.remove(output_path)

# Main function to run the bot
def main():
    try:
        print("Starting bot...")
        application = Application.builder().token(API_TOKEN).build()

        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.VOICE, handle_voice))

        # Start the bot
        application.run_polling()
        print("Bot is running...")
    except Exception as e:
        print(f"Error starting the bot: {e}")

if __name__ == "__main__":
    main()
