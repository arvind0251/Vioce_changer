import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Function to process voice and change pitch
def change_voice(input_file, output_file):
    sound = AudioSegment.from_file(input_file, format="ogg")
    # Increase pitch
    octaves = 0.5
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
    sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    sound = sound.set_frame_rate(44100)
    sound.export(output_file, format="ogg")

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
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
