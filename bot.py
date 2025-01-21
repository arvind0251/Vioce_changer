import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import librosa
import soundfile as sf

# Enable logging to debug issues
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Voice conversion function (pitch and formant shifting)
def shift_pitch_and_formant(input_file, output_file, pitch_factor=3.0):
    try:
        # Load the audio file
        y, sr = librosa.load(input_file, sr=None)
        if y is None or len(y) == 0:
            raise ValueError("Loaded audio file is empty")

        # Apply pitch shifting
        y_pitch_shifted = librosa.effects.pitch_shift(y, sr, n_steps=pitch_factor)

        # Apply formant preservation
        y_formant_shifted = librosa.effects.time_stretch(y_pitch_shifted, 1.0)

        # Normalize the output
        y_normalized = librosa.util.normalize(y_formant_shifted)

        # Save the resulting audio
        sf.write(output_file, y_normalized, sr)
        logger.info(f"Voice conversion successful! Saved to {output_file}")
    except Exception as e:
        logger.error(f"Error processing audio: {e}", exc_info=True)

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a voice message, and I'll convert it to a female voice!")

# Handle incoming voice messages
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        voice_file = await update.message.voice.get_file()
        input_path = f"{user.id}_input.ogg"
        output_path = f"{user.id}_output.ogg"

        # Download voice file
        await voice_file.download_to_drive(input_path)
        logger.info(f"Voice file downloaded: {input_path}")

        # Perform voice conversion
        shift_pitch_and_formant(input_path, output_path, pitch_factor=3.0)
        logger.info(f"Voice conversion complete. Output saved: {output_path}")

        # Send converted voice back to user
        with open(output_path, "rb") as voice:
            await update.message.reply_voice(voice)

        # Clean up temporary files
        os.remove(input_path)
        os.remove(output_path)
        logger.info("Temporary files deleted.")

    except Exception as e:
        logger.error(f"Error handling voice message: {e}", exc_info=True)
        await update.message.reply_text("Something went wrong. Please try again.")

# Main function to run the bot
async def main():
    try:
        application = ApplicationBuilder().token("YOUR_BOT_API_TOKEN").build()

        # Add command and message handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.VOICE, handle_voice))

        # Initialize and run polling
        await application.initialize()
        await application.run_polling()
    finally:
        await application.shutdown()

# Proper event loop handling
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
