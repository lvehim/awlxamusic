import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import asyncio

# Bot token and Spotify credentials
TOKEN = 'YOUR_BOT_TOKEN'
SPOTIFY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID'
SPOTIFY_CLIENT_SECRET = 'YOUR_SPOTIFY_CLIENT_SECRET'

# Configure Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# Configure bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Premium users list and your ID
premium_users = set()
YOUR_DISCORD_ID = 123456789012345678 # Replace with your actual Discord ID

class YTDLSource(discord.PCMVolumeTransformer):
    @classmethod
    async def from_spotify(cls, track_url, *, loop=None):
        results = sp.track(track_url)
        track_name = results['name']
        artists = ', '.join([artist['name'] for artist in results['artists']])
        search_query = f"{track_name} {artists} lyrics"

        ytdl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True
        }

        with YoutubeDL(ytdl_opts) as ytdl:
            info = ytdl.extract_info(f"ytsearch:{search_query}", download=False)['entries'][0]
            url = info['formats'][0]['url']
            return cls(discord.FFmpegPCMAudio(url), data=info)


# Event: On Bot Ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


# Command: Join voice channel
@bot.command(name='join')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return
    else:
        channel = ctx.message.author.voice.channel
