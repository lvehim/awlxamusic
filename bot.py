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
        channel = ctx.message.author.voice.channel await channel.connect()


# Command: Leave voice channel
@bot.command(name='leave')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


# Command: Play track from Spotify
@bot.command(name='play')
async def play(ctx, url: str):
    if not url.startswith('https://open.spotify.com/track/'):
        await ctx.send("Please provide a valid Spotify track URL.")
        return

    voice_client = ctx.message.guild.voice_client
    if not voice_client:
        await ctx.send("The bot is not connected to a voice channel.")
        return

    async with ctx.typing():
        player = await YTDLSource.from_spotify(url, loop=bot.loop)
        voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

    await ctx.send(f'Now playing: {player.title}')


# Command: 24/7 Mode
@bot.command(name='247')
async def mode_247(ctx):
    if ctx.author.id not in premium_users:
        await ctx.send("This feature is available for premium users only.")
        return

    await ctx.send("24/7 mode enabled. The bot will stay connected even when idle.")


# Command: Add premium user
@bot.command(name='addpremium')
async def add_premium(ctx, user: discord.User):
    if ctx.author.id != YOUR_DISCORD_ID:
        await ctx.send("You do not have permission to use this command.")
        return

    premium_users.add(user.id)
    await ctx.send(f"User {user.name} has been added to premium users.")


# Command: Remove premium user
@bot.command(name='removepremium')
async def remove_premium(ctx, user: discord.User):
    if ctx.author.id != YOUR_DISCORD_ID:
        await ctx.send("You do not have permission to use this command.")
        return

    premium_users.discard(user.id)
    await ctx.send(f"User {user.name} has been removed from premium users.")
