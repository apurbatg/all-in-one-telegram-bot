import os

import logging

from telegram import Update, Bot

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from pytube import YouTube

import instaloader

from tqdm import tqdm

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

def error_handler(update: Update, context: CallbackContext):

    """Log the error and send a message to the user."""

    logger.warning('Update "%s" caused error "%s"', update, context.error)

    update.message.reply_text('Oops! Something went wrong. Please try again later.')

def start(update: Update, context: CallbackContext):

    """Send a message when the command /start is issued."""


def download_video(update: Update, context: CallbackContext):

    """Download a video from a YouTube or Instagram link."""

    link = update.message.text

    if "youtube" in link:

        try:

            yt = YouTube(link)

            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            filename = yt.title + ".mp4"

            filesize = stream.filesize

            with open(filename, 'wb') as f:

                progress_callback = lambda bytes_remaining, file_size: tqdm(total=file_size, initial=file_size - bytes_remaining, unit='B', unit_scale=True, desc=filename)

                stream.download(output_path=".", filename=filename, progress_callback=progress_callback)

            update.message.reply_text(f"Video downloaded successfully: {filename}")

        except Exception as e:

            logger.error(str(e))

            update.message.reply_text(f"Oops! An error occurred while downloading the video.")

    elif "instagram" in link:

        try:

            L = instaloader.Instaloader()

            post = instaloader.Post.from_shortcode(L.context, link.split("/")[-2])

            filename = post.owner_username + "-" + post.date.strftime("%Y-%m-%d") + ".mp4"

            with open(filename, 'wb') as f:

                progress_bar = tqdm(unit="B", total=post.video_url_info.get("video_versions")[0]["content_length"], desc=filename)

                f.write(post.video_url.read(progress_bar.update))

            update.message.reply_text(f"Video downloaded successfully: {filename}")

        except Exception as e:

            logger.error(str(e))

            update.message.reply_text(f"Oops! An error occurred while downloading the video.")

    else:

        update.message.reply_text("I'm sorry, I don't recognize that link.")

# create the Updater and pass in the bot token and error handler

updater = Updater(token=os.environ.get("BOT_TOKEN"), use_context=True)

updater.dispatcher.add_error_handler(error_handler)

# add your handlers to the dispatcher

updater.dispatcher.add_handler(CommandHandler("start", start))

updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)').compile(), download_video))

updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'https?://(?:www\.)?(?:instagram\.com/p/|instagr\.am/p/)([\w-]+)').compile(), download_video))

# start the bot

updater.start_polling()

updater.idle()

