import os
import logging
import pytube
import instaloader
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from tqdm import tqdm


# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)


# Define the start command handler
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Hi! Send me a YouTube or Instagram video link and I\'ll send you the download link.')


# Define the video download handler
def download_video(update, context):
    try:
        # Get the video link from the message
        video_link = update.message.text

        if 'youtube' in video_link:
            # Create a PyTube object for the video
            youtube_video = pytube.YouTube(video_link)

            # Get the highest resolution stream
            video_stream = youtube_video.streams.get_highest_resolution()

            # Get the video title
            video_title = youtube_video.title

            # Download the video
            video_path = video_stream.download()

            # Send the video file to the user with progress bar
            with open(video_path, 'rb') as video_file:
                context.bot.send_video(chat_id=update.effective_chat.id,
                                       video=video_file,
                                       caption=f'Download complete: {video_title}',
                                       timeout=120,
                                       progress=progress_callback)

            # Delete the video file from the local system
            os.remove(video_path)

        elif 'instagram' in video_link:
            # Create an Instaloader object for the video
            instaloader_obj = instaloader.Instaloader()

            # Download the video
            video_filename = instaloader_obj.download_video(video_link)

            # Get the video title
            video_title = instaloader_obj.context.item_caption

            # Send the video file to the user with progress bar
            with open(video_filename, 'rb') as video_file:
                context.bot.send_video(chat_id=update.effective_chat.id,
                                       video=video_file,
                                       caption=f'Download complete: {video_title}',
                                       timeout=120,
                                       progress=progress_callback)

            # Delete the video file from the local system
            os.remove(video_filename)

    except Exception as e:
        logger.error(e, exc_info=True)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oops! Something went wrong. Please try again later.')


# Define a progress bar callback function
def progress_callback(current, total):
    percentage = int((current / total) * 100)
    text = f'Downloading... {percentage}%'
    tqdm.write(text, end='\r')


# Define the main function
def main():
    # Get the bot token from the environment variable
    bot_token = os.environ.get('BOT_TOKEN')

    # Create an Updater object with the bot token
    updater = Updater(token=bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the start command handler
    dp.add_handler(CommandHandler('start', start))

    # Register the video download handler
    dp.add_handler(MessageHandler(Filters.regex('^https?://(?:www\.)?(youtube|instagram)\.com/'), download_video))

    # Start the bot
    updater.start_polling()

    # Run the bot until Ctrl-C is pressed or the process receives SIGINT, SIGTERM or SIGAB
