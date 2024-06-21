import os
import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_dl import YoutubeDL
import asyncio

# Load environment variables from Replit secrets
TOKEN = os.getenv('DISCORD_TOKEN')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
YOUR_USER_ID = int(os.getenv('BOT_OWNER_ID'))

# Configure Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

# Configure bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
}
ytdl = YoutubeDL(ytdl_opts)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
    
    @classmethod
    async def from_spotify(cls, track_url, *, loop=None):
        results = sp.track(track_url)
        track_name = results['name']
        artists = ', '.join([artist['name'] for artist in results['artists']])
        search_query = f"{track_name} {artists} lyrics"
        
        ytdl_opts = {'format': 'bestaudio'}
        with YoutubeDL(ytdl_opts) as ytdl:
            info = ytdl.extract_info(f"ytsearch:{search_query}", download=False)['entries'][0]
            url = info['formats'][0]['url']
            return cls(discord.FFmpegPCMAudio(url), data=info)

premium_users = set()

def is_owner(ctx):
    return ctx.author.id == YOUR_USER_ID

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='join')
async def join(ctx):
    if not ctx.message.author.voice:
