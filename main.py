import os
import logging
import pytube
from telegram import ChatAction, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define the callback function for the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Send me a YouTube video link and I'll upload the video file.")

# Define the callback function for handling text messages
def text_handler(update, context):
    # Check if the message contains a YouTube video link
    if 'youtube.com/watch?v=' in update.message.text:
        # Send a "typing" action to the user
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        # Download the video file
        yt = pytube.YouTube(update.message.text)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        file_path = stream.download()
        # Calculate the file size
        file_size = os.path.getsize(file_path)
        # Upload the video file with a progress bar
        with open(file_path, 'rb') as f:
            progress = 0
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)
                context.bot.send_video(chat_id=update.effective_chat.id, video=InputFile(file_path), caption='Uploading...', supports_streaming=True, timeout=600)
                progress += len(chunk)
                percentage = progress / file_size * 100
                context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.message.message_id, text=f"Uploading... {percentage:.1f}%")
        # Delete the downloaded file
        os.remove(file_path)
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.message.message_id, text="Upload complete!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please send a valid YouTube video link.")

# Set up the Telegram bot
updater = Updater(token='6044904531:AAGvifbBd2dMbjjJN2ANOhcJX-dq3eeDRB0', use_context=True)

# Set up the command handlers
updater.dispatcher.add_handler(CommandHandler('start', start))

# Set up the message handlers
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))

# Start the bot
updater.start_polling()
updater.idle()
