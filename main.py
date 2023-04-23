import os

import telegram

from telegram.ext import Updater, CommandHandler

import pytube

import instaloader

import praw

BOT_TOKEN = '6044904531:AAGvifbBd2dMbjjJN2ANOhcJX-dq3eeDRB0'

def start(update, context):

    """Send a welcome message when the command /start is issued."""

    update.message.reply_text('Hi! Send me a YouTube, Instagram or Reddit video URL and I will download it for you.')

def download_video(update, context):

    """Download a YouTube, Instagram or Reddit video and send it to the user."""

    url = context.args[0] # Get the video URL from the user's message

    if 'youtube.com' in url:

        # Download a YouTube video

        video = pytube.YouTube(url).streams.get_highest_resolution()

        video.download() # Download the video to the current directory

        video_file = open(video.default_filename, 'rb') # Open the video file

        update.message.reply_video(video=video_file) # Send the video to the user

        video_file.close() # Close the file

    elif 'instagram.com' in url:

        # Download an Instagram video

        insta = instaloader.Instaloader()

        insta.download_video(url) # Download the video to the current directory

        video_file = open(insta.context.filename, 'rb') # Open the video file

        update.message.reply_video(video=video_file) # Send the video to the user

        video_file.close() # Close the file

    elif 'reddit.com' in url:

        # Download a Reddit video

        reddit = praw.Reddit(client_id='YOUR_CLIENT_ID',

                             client_secret='YOUR_CLIENT_SECRET',

                             username='YOUR_REDDIT_USERNAME',

                             password='YOUR_REDDIT_PASSWORD',

                             user_agent='YOUR_USER_AGENT')

        submission = reddit.submission(url=url)

        video_url = submission.media['reddit_video']['fallback_url']

        video_file = open('reddit_video.mp4', 'wb')

        video_file.write(requests.get(video_url).content)

        video_file.close()

        video_file = open('reddit_video.mp4', 'rb')

        update.message.reply_video(video=video_file) # Send the video to the user

        video_file.close()

    else:

        # Invalid URL

        update.message.reply_text('Invalid URL. Please send me a valid YouTube, Instagram or Reddit video URL.')

def main():

    """Start the bot."""

    updater = Updater(token='YOUR_BOT_TOKEN', use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_handler(CommandHandler('download_video', download_video))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':

    main()

