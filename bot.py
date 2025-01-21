import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
from pydub import AudioSegment
from dotenv import load_dotenv

# Set ffmpeg and ffprobe path
AudioSegment.converter = os.getenv('FFMPEG_BINARY', 'ffmpeg')
AudioSegment.ffprobe = os.getenv('FFPROBE_BINARY', 'ffprobe')

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Function to process voice and change pitch
def change_voice(input_file, output_file):
    """
    Adjust the pitch of the input voice to mimic a bot-like sound similar to the user's provided example.
    """
    sound = AudioSegment.from_file(input_file, format="ogg")

    # Pitch adjustment logic
    octaves = 0.8  # Similar to provided example; adjust for bot-like voice
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
    sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    sound = sound.set_frame_rate(44100)  # Standard sample rate for output

    # Export the processed audio
    sound.export(output_file, format="ogg")

# Command to start the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Mujhe apna voice message bhejiye, main usse ladki ki voice mein badal dunga!")

# Handle voice messages
async def handle_voice(update: Update, context: CallbackContext):
    user = update.message.from_user
    voice_file = await update.message.voice.get_file()
    input_path = f"{user.id}_input.ogg"
    output_path = f"{user.id}_output.ogg"

    # Download voice file
    await voice_file.download_to_drive(input_path)

    # Change voice pitch
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
        # Initialize the application
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
