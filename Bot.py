import os
import telegram
import requests
import google.auth
from googleapiclient.discovery import build
import youtube_dl

# Get the bot token from the environment
BOT_TOKEN = os.environ['BOT_TOKEN']

# Initialize the bot
bot = telegram.Bot(token=BOT_TOKEN)

# Authenticate with the Google API
scopes = ["https://www.googleapis.com/auth/youtube.upload"]
credentials, project = google.auth.default(scopes=scopes)
youtube = build("youtube", "v3", credentials=credentials)

# Define a handler function that will be called when a new message arrives
def handle_message(message):
    # Check if the message contains a video
    if message.video:
        # Download the video
        video_file = bot.get_file(message.video.file_id)
        video_url = video_file.file_path
        response = requests.get(video_url)
        with open("video.mp4", "wb") as f:
            f.write(response.content)
        
        # Convert the video to a YouTube short
        with youtube_dl.YoutubeDL({"format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]"}) as ydl:
            result = ydl.extract_info("video.mp4", download=False)
            youtube_url = result['url']
        
        # Upload the YouTube short to your YouTube channel
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": "My YouTube Short",
                    "description": "A short video uploaded from Telegram",
                    "categoryId": 22,
                },
                "status": {
                    "privacyStatus": "public",
                },
            },
            media_body=youtube_url
        )
        response = request.execute()
        
        # Send a message to the user with the URL of the YouTube short
        video_id = response["id"]
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        bot.send_message(chat_id=message.chat_id, text=youtube_url)

# Start the bot
bot.set_update_listener(handle_message)
bot.polling()
