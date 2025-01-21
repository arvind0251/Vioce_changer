import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
from pydub import AudioSegment
from dotenv import load_dotenv
from voice_cloning.generation import *  # Import the voice cloning functions

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Function to process voice and change voice using voice cloning
def change_voice(input_file, output_file):
    # Load the reference voice file (ensure you have a reference female voice)
    reference_voice_path = "path/to/your/reference_female_voice.wav"  # Update this path
    speech_text = "Your transformed voice message"  # Customize this as needed

    # Generate the cloned voice
    generated_wav = speech_generator(
        voice_type="western",  # or "indian"
        sound_path=reference_voice_path,
        speech_text=speech_text
    )

    # Save the generated voice to the output file
    save_sound(generated_wav, filename=output_file, noise_reduction=True)

# Command to start the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Mujhe apna voice message bhejiye, main usse ladki ki voice mein badal dunga!")

# Handle voice messages
async def handle_voice(update: Update, context: CallbackContext):
    user = update.message.from_user
    voice_file = await update.message.voice.get_file()
    input_path = f"{user.id}_input.ogg"
    output_path = f"{user.id}_output.wav"  # Change to .wav for compatibility

    # Download voice file
    await voice_file.download_to_drive(input_path)

    # Change voice using voice cloning
    change_voice(input_path, output_path)

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

        # Check if token is valid
        if not API_TOKEN:
            raise ValueError("TELEGRAM_API_TOKEN is missing. Please check your environment variables.")

        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.VOICE, handle_voice))

        # Start the bot using run_polling()
        application.run_polling()
        print("Bot is running...")
    except Exception as e:
        print(f"Error starting the bot: {e}")

if __name__ == "__main__":
    main()
