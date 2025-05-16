import asyncio
import discord
import yt_dlp
from discord.ext import commands
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from queue import Queue

# dot env load
load_dotenv()

# get token
discord_token = os.getenv('DISCORD_BOT_TOKEN')
youtube_api_key = os.getenv('YOUTUBE_API_KEY')
ffmpeg_path = os.getenv('FFMPEG_Path')
dl_path = os.getenv('MUSIC_PATH')

if not discord_token or not youtube_api_key or not ffmpeg_path or not dl_path:
    print("Error .env")
    exit(1)

# play list
music_list = Queue()

# discord
intents = discord.Intents.default()  # intents active
intents.messages = True  # set react to message event
intents.guilds = True  # set react to server(guild) event
intents.message_content = True  # set read message

# ! + query
bot = commands.Bot(command_prefix='!', intents=intents)


# function , YouTube api search
async def youtube_search(ctx, query):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)

    request = youtube.search().list(
        q=query,
        part='snippet',
        type='music',
        maxResults=1
    )
    response = request.execute()

    if response['items']:
        return f'https://www.youtube.com/watch?v={response["items"][0]["id"]["videoId"]}'
    else:
        await ctx.send(f"Failed... no search result")
        return None


# play music
async def start_playback(ctx):
    while music_list.qsize() > 0:
        music_data = music_list.get()
        audio_source = discord.FFmpegPCMAudio(executable=ffmpeg_path, source=music_data.get('url', 'noData'))
        ctx.voice_client.play(audio_source)
        await ctx.send(f"play music: {music_data.get('name', 'noData')}")
        while ctx.voice_client.is_playing():
            await asyncio.sleep(1)
        ctx.voice_client.stop()
        os.remove(music_data['url'])
    await ctx.voice_client.disconnect()
    await ctx.send('End play music')


# client setting
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


# add reaction to hello
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('hello!')


# add music from YouTube
@bot.command(name='add')
async def search(ctx, *, query):
    video_id = await youtube_search(ctx, query)
    if video_id:
        ydl_opts = {
            'headers': {
                'User-Agent': 'Mozilla/5.0'
            },
            'format': 'bestaudio/best',
            'outtmpl': f'{dl_path}/%(title)s.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_id, download=True)
            info = ydl.sanitize_info(info)
            if info['title'] and info['ext']:
                music_path = f"{dl_path}/{info['title']}.{info['ext']}"
                musicData = {'name': query, 'url': music_path}
                music_list.put(musicData)
                await ctx.send(f"add music {query}")
            else:
                await ctx.send("Failed... to add music")

    else:
        await ctx.send('Failed... no search data')

# play music
@bot.command(name='play')
async def play(ctx):
    if not music_list.empty():
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send('Failed... already played')
            return
        await start_playback(ctx)
    else:
        await ctx.send('Failed... no data')

bot.run(discord_token)
