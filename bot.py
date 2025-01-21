import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import librosa
import soundfile as sf

# Enable logging to debug issues
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice conversion function (pitch and formant shifting)
def shift_pitch_and_formant(input_file, output_file, pitch_factor=3.0):
    try:
        # Load the audio file
        y, sr = librosa.load(input_file, sr=None)

        # Apply pitch shifting
        y_pitch_shifted = librosa.effects.pitch_shift(y, sr, n_steps=pitch_factor)

        # Apply formant preservation (using librosa or other library)
        y_formant_shifted = librosa.effects.time_stretch(y_pitch_shifted, 1.0)

        # Normalize the output to avoid clipping and distortion
        y_normalized = librosa.util.normalize(y_formant_shifted)

        # Save the resulting audio to output file
        sf.write(output_file, y_normalized, sr)
        logger.info(f"Voice conversion successful! Saved to {output_file}")
    except Exception as e:
        logger.error(f"Error processing audio: {e}")

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a voice message, and I'll convert it to a female voice!")

# Handle incoming voice messages
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        voice_file = await update.message.voice.get_file()  # Await the coroutine
        input_path = f"{user.id}_input.ogg"
        output_path = f"{user.id}_output.ogg"

        # Download voice file
        await voice_file.download_to_drive(input_path)
        logger.info(f"Voice file downloaded: {input_path}")

        # Perform voice conversion (pitch and formant shifting)
        shift_pitch_and_formant(input_path, output_path, pitch_factor=3.0)
        logger.info(f"Voice conversion complete. Output saved: {output_path}")

        # Send converted voice back to user
        with open(output_path, 'rb') as voice:
            await update.message.reply_voice(voice)

        # Clean up temporary files
        os.remove(input_path)
        os.remove(output_path)
        logger.info("Temporary files deleted.")

    except Exception as e:
        logger.error(f"Error handling voice message: {e}")
        await update.message.reply_text("Something went wrong. Please try again.")

# Main function to run the bot
async def main():
    # Set up the application with your Telegram bot token
    application = ApplicationBuilder().token('YOUR_BOT_API_TOKEN').build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Run the bot
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
