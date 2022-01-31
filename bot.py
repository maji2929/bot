# bot.py
from logging import StrFormatStyle
import os
import random

import discord
from discord import permissions
from discord.client import Client
from dotenv import load_dotenv
from discord.ext import commands
import requests
from requests import get
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import datetime
from discord import FFmpegPCMAudio
from discord.utils import get
from discord import TextChannel
from googletrans import Translator, constants
import json
from textblob import TextBlob
import urllib
import youtube_dl
from pycoingecko import CoinGeckoAPI
import time
import discordhex
from cogwatch import watch
from keep_alive import keep_alive



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API = 'https://api.genshin.dev/{}'

cg = CoinGeckoAPI()
char = API.format("characters/{}")
art = API.format("artifacts/{}")
wp = API.format("weapons/{}")
imgc = 'https://rerollcdn.com/GENSHIN/Characters/{}.png'
imga = 'https://rerollcdn.com/GENSHIN/Gear/{}.png'
imgw = 'https://rerollcdn.com/GENSHIN/Weapon/NEW/{}.png'

charlist = requests.get('https://api.genshin.dev/characters').text
cl = json.loads(charlist)
artlist = requests.get('https://api.genshin.dev/artifacts').text
al = json.loads(artlist)
wplist = requests.get('https://api.genshin.dev/weapons').text
wl = json.loads(wplist)

def get(element:str):
  path = os.path.abspath("./conf.json")
  with open(path, "r") as read_file:
    content = json.load(read_file)
  return content[element]
  
intents = discord.Intents.all()
client = discord.Client(intents=intents)
permissions = discord.Permissions.all()
bot = commands.Bot(command_prefix='?', intents=intents, help_command=None, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False), permissions=permissions)
time = datetime.datetime.utcnow()
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join_voice(self, ctx):
    connected = ctx.author.voice
    if connected:
        await connected.channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='play', aliases=['p'], help='To play a song from youtube')
async def play(ctx,url):
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.event
async def on_ready():
    print(f'{bot.user.name} dh login')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, Welcome aboard!'
    )

# check song from spotify
@bot.command(name='check', help='Check song from spotify')
async def check_song(ctx, song_name: str):
    url = 'https://api.spotify.com/v1/search?q=' + song_name + '&type=track'
    response = requests.get(url, headers={"Authorization": "Bearer " + get('SPOTIFY_TOKEN')})
    data = response.json()
    try:
        title = data['tracks']['items'][0]['name']
        artist = data['tracks']['items'][0]['artists'][0]['name']
        album = data['tracks']['items'][0]['album']['name']
        preview_url = data['tracks']['items'][0]['preview_url']
        await ctx.send(f'Title: {title}\nArtist: {artist}\nAlbum: {album}\nPreview: {preview_url}')
    except Exception as e:
        print(e)
        await ctx.send('Song not found!')

#info bot   
@bot.command(name='infobot', help='Show bot info')
async def info(ctx):
    embed = discord.Embed(title='Info Bot')
    embed.add_field(name='Name', value=bot.user.name, inline=False)
    embed.add_field(name='ID', value=bot.user.id, inline=False)
    embed.add_field(name='Prefix', value='?', inline=False)
    #created at
    embed.add_field(name='Created at', value=bot.user.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name='Created by', value='[<@325260673015873548>](https://github.com/Raynald22)', inline=False)
    embed.add_field(name ='Invite', value = "[Click Here](https://discord.com/api/oauth2/authorize?client_id=765150186431315987&permissions=8&scope=bot)", inline = True)

    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
    # footer made by @Tartaglia with url
    await ctx.send(embed=embed)




@bot.command(name='rickroll', help='Rickrolls the user')
async def rickroll(ctx):
    embed=discord.Embed(title="Get Rickrolled, lmao!", url="", description="**That's the Handsome Rick Astley**")
    embed.set_image(url="https://c.tenor.com/u9XnPveDa9AAAAAM/rick-rickroll.gif")
    await ctx.reply(embed=embed) 


    
# Info Server command
@bot.command(name='info', help='Shows the server info')
async def info(ctx):
    embed=discord.Embed(title="Server Info", url="")
    embed.add_field(name="Server Name", value=ctx.guild.name, inline=False)
    embed.add_field(name="Server ID", value=ctx.guild.id, inline=False)
    embed.add_field(name="Server Owner", value=ctx.guild.owner, inline=False)
    embed.add_field(name="Server Region", value=ctx.guild.region, inline=False)
    # created_at dd/mm/yyyy
    embed.add_field(name="Server Created", value=ctx.guild.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="Server Member Count", value=ctx.guild.member_count, inline=False)
    embed.add_field(name="Server Role Count", value=len(ctx.guild.roles), inline=False)
    embed.add_field(name="Server Emote Count", value=len(ctx.guild.emojis), inline=False)
    # get avatar server
    embed.set_thumbnail(url=ctx.guild.icon_url)
    await ctx.send(embed=embed)

# Info User with avatar command
@bot.command(name='userinfo', aliases=['user', 'ui', 'profile'], help='Shows the user info')
async def userinfo(ctx, member: discord.Member):
    embed=discord.Embed(title="User Info", url="")
    embed.add_field(name="Name", value=member.name, inline=False)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Nickname", value=member.nick, inline=False)
    roles = [role for role in member.roles[1:]]
    embed.add_field(name=f'Roles ({len(roles)}):', value="".join([role.mention + "|" for role in roles]), inline=False)
    embed.add_field(name="Created At", value=member.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="Joined At", value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
    #status
    if member.status == discord.Status.online:
        embed.add_field(name="Status", value="Online", inline=False)
    elif member.status == discord.Status.offline:
        embed.add_field(name="Status", value="Offline", inline=False)
    elif member.status == discord.Status.idle:
        embed.add_field(name="Status", value="Idle", inline=False)
    elif member.status == discord.Status.dnd:
        embed.add_field(name="Status", value="Do Not Disturb", inline=False)
    #game
    if member.activity:
        if member.activity.type == discord.ActivityType.playing:
            embed.add_field(name="Playing", value=member.activity.name, inline=False)
        elif member.activity.type == discord.ActivityType.streaming:
            embed.add_field(name="Streaming", value=member.activity.name, inline=False)
        elif member.activity.type == discord.ActivityType.listening:
            embed.add_field(name="Listening", value=member.activity.name, inline=False)
        elif member.activity.type == discord.ActivityType.watching:
            embed.add_field(name="Watching", value=member.activity.name, inline=False)
    else:
        embed.add_field(name="Playing", value="None", inline=False)
    # Status Premium
    if member.premium_since:
        embed.add_field(name="Premium since", value=member.premium_since, inline=False)
    else:
        embed.add_field(name="Premium since", value="None", inline=False)
    
    embed.set_thumbnail(url=member.avatar_url)
    await ctx.reply(embed=embed)

# covid-19 in indonesiacommand
@bot.command(name='covid', help='Gives info about covid-19 in indonesia')
async def covid(ctx):
    url = "https://api.kawalcorona.com/indonesia"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    embed=discord.Embed(title="Covid-19 in Indonesia", url="")
    embed.add_field(name="Positif", value=data[0]['positif'], inline=True)
    embed.add_field(name="Sembuh", value=data[0]['sembuh'], inline=True)
    embed.add_field(name="Meninggal", value=data[0]['meninggal'], inline=True)
    embed.add_field(name="Dirawat", value=data[0]['dirawat'], inline=True)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/746165212586768586/746165212586768586.png")
    await ctx.reply(embed=embed)

# wikipedia https://id.wikipedia.org/api/rest_v1/page/summary/
@bot.command(name='wiki', help='Gives info about wikipedia')
async def wiki(ctx, *, search):
    url = "https://id.wikipedia.org/api/rest_v1/page/summary/{}".format(search)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    if data['type'] == 'disambiguation':
        embed=discord.Embed(title="Wikipedia", url="")
        embed.add_field(name="Disambiguation", value="Please choose one of the following", inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/746165212586768586/746165212586768586.png")
        await ctx.reply(embed=embed)
        for item in data['redirects']:
            embed=discord.Embed(title="Wikipedia", url="")
            embed.add_field(name="Disambiguation", value=item['to'], inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/746165212586768586/746165212586768586.png")
            await ctx.reply(embed=embed)
    else:
        embed=discord.Embed(title="Wikipedia", url="", description=data['title'])
        embed.add_field(name="Deskripsi", value=data['extract'], inline=False)
        embed.set_image(url=data['originalimage']['source'])
        embed.add_field(name="URL", value=data['content_urls']['desktop']['page'], inline=False)
        # set footer by user
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

#server icon command
@bot.command(name='servericon', help='Gives the server icon')
async def servericon(ctx):
    embed=discord.Embed(title="Server Icon", url="")
    embed.set_image(url=ctx.guild.icon_url)
    await ctx.reply(embed=embed)

#avatar member command
@bot.command(name='avatar', help='Gives the avatar of the member')
async def avatar(ctx, member: discord.Member):
    embed=discord.Embed(title="Avatar", url="")
    embed.set_image(url=member.avatar_url)
    await ctx.reply(embed=embed)

# purge message command
@bot.command(name='purge', delete_after=3)
@commands.has_role('ORANG DALAM')
async def purge(ctx, limit=100, member: discord.Member=None):
    await ctx.message.delete()
    msg = []
    try:
        limit = int(limit)
    except:
        return await ctx.send("Please pass in an integer as limit")
    if not member:
        await ctx.channel.purge(limit=limit)
        return await ctx.send(f"Purged {limit} messages", delete_after=3)
    async for m in ctx.channel.history():
        if len(msg) == limit:
            break
        if m.author == member:
            msg.append(m)
    await ctx.channel.delete_messages(msg)
    await ctx.send(f"Purged {limit} messages of {member.mention}", delete_after=3)
    

# get list trending movie command
@bot.command(name='trendingmovie', help='Gives the list of trending movies')
async def trending(ctx):
    url = "https://api.themoviedb.org/3/trending/movie/week?api_key=b4f4d1c2f91c4d46cc9f8dfd603919ff"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    embed=discord.Embed(title="Trending Movies", url="")
    for i in range(len(data['results'])):
        embed.add_field(name=f'{i+1} - {data["results"][i]["title"]}', value=f'Rating: {data["results"][i]["vote_average"]}', inline=False)
        #release date
        embed.add_field(name="Release Date", value=data["results"][i]["release_date"], inline=False)
    await ctx.reply(embed=embed)

# get movie info command
@bot.command(name='movie', help='Gives the info of the movie')
async def movie(ctx, *, movie: str):
    url = "https://api.themoviedb.org/3/search/movie?api_key=b4f4d1c2f91c4d46cc9f8dfd603919ff&language=en-US&query=" + movie + "&page=1&include_adult=false"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    embed=discord.Embed(title="Movie Info", url="")
    embed.add_field(name="Title", value=data['results'][0]['title'], inline=False)
    embed.add_field(name="Overview", value=data['results'][0]['overview'], inline=False)
    embed.add_field(name="Rating", value=data['results'][0]['vote_average'], inline=False)
    embed.add_field(name="Release Date", value=data['results'][0]['release_date'], inline=False)
    # thumbnail
    embed.set_thumbnail(url=f"https://image.tmdb.org/t/p/w500{data['results'][0]['poster_path']}")
    await ctx.reply(embed=embed)

# get random meme
@bot.command(name='meme', help='Gives a random meme')
async def meme(ctx):
    url = "https://meme-api.herokuapp.com/gimme"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    embed=discord.Embed(title="Meme", url="")
    embed.set_image(url=data['url'])
    await ctx.reply(embed=embed)

# filter avatar to grey
@bot.command(name='grey', help='Gives the avatar of the member with the specified filter')
async def avatarfilter(ctx, member: discord.Member):
    embed=discord.Embed(title="Avatar", url="")
    embed.set_image(url=f"https://res.cloudinary.com/demo/image/fetch/w_200,e_grayscale/{member.avatar_url}?size=1024")
    await ctx.reply(embed=embed)

# filter avatar to 90 degrees
@bot.command(name='flip', help='Gives the avatar of the member with the specified filter')
async def avatarfilter(ctx, member: discord.Member):
    embed=discord.Embed(title="Avatar", url="")
    embed.set_image(url=f"https://res.cloudinary.com/demo/image/fetch/w_200,a_90/{member.avatar_url}?size=1024")
    await ctx.reply(embed=embed)

# get today's date
@bot.command(name='today', help='Gives the current date')
async def date(ctx):
    embed=discord.Embed(title="Date", url="")
    # get day
    embed.add_field(name="Day", value=datetime.datetime.now().strftime("%A"), inline=False)
    embed.add_field(name="Today's Date", value=datetime.datetime.now().strftime("%d-%m-%Y"), inline=False)
    # get time
    embed.add_field(name="Time", value=datetime.datetime.now().strftime("%H:%M:%S"), inline=False)
    await ctx.reply(embed=embed)

# respond message member
@bot.command(name='pungky')
async def respond(ctx):
    await ctx.reply(f'lom mndi')

# mention member with message
@bot.command(name='mention')
async def mention(ctx, member: discord.Member):
    await ctx.reply(f'{member.mention} bau')

@bot.command(name='sa')
async def respond(ctx):
    await ctx.reply(f'♥♥♥♥♥♥♥')

# afk and if user typing, back to normal
@bot.command(name='afk')
async def afk(ctx, *, reason: str):
    await ctx.send(f"{ctx.author.mention} is now AFK. {reason}")
    await ctx.trigger_typing()
    await ctx.send(f"{ctx.author.mention} is back!")

# get weather 
@bot.command(name='weather', help='Gives the weather')
async def weather(ctx, *, city: str):
    url = "https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=32b2bc6c49f9407597e4139767efaee8"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    embed=discord.Embed(title="Weather", url="")
    # reqested by author name, avatar, time
    embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
    embed.add_field(name="City", value=city, inline=False)
    #format temperature decimal
    embed.add_field(name="Temperature", value=f'{data["main"]["temp"]-273.15:.2f} °C', inline=False)
    embed.add_field(name="Description", value=data['weather'][0]['main'], inline=False)
    embed.add_field(name="Wind Speed", value=data['wind']['speed'], inline=False)
    embed.add_field(name="Humidity", value=data['main']['humidity'], inline=False)
    embed.add_field(name="Pressure", value=data['main']['pressure'], inline=False)
    #timezome
    embed.add_field(name="Timezone", value=data['timezone'], inline=False)
    # set thumbnail
    embed.set_thumbnail(url=f"https://openweathermap.org/img/w/{data['weather'][0]['icon']}.png")
    await ctx.reply(embed=embed)

# get random quote
@bot.command(name='quote', help='Gives a random quote')
async def quote(ctx):
    url = "https://api.forismatic.com/api/1.0/?method=getQuote&lang=en&format=json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    embed=discord.Embed(title="", url="")
    
    embed.add_field(name="Quote", value=data["*quoteText*"], inline=False)
    embed.add_field(name="Author", value=data["quoteAuthor"], inline=False)
    await ctx.reply(embed=embed)

# get pokemon info
@bot.command(name='pokemon', help='Gives the pokemon info')
async def pokemon(ctx, *, pokemon: str):
    url = "https://pokeapi.co/api/v2/pokemon/" + pokemon
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    embed=discord.Embed(title="Pokemon", url="")
    # get pokemon name uppercase
    embed.add_field(name="Name", value=data['name'].upper(), inline=False)
    embed.add_field(name="Weight", value=data['weight'], inline=False)
    embed.add_field(name="Height", value=data['height'], inline=False)
    embed.add_field(name="Abilities", value=data['abilities'][0]['ability']['name'], inline=False)
    embed.add_field(name="Type", value=data['types'][0]['type']['name'].upper(), inline=False)
    embed.add_field(name="Type", value=data['types'][1]['type']['name'].upper(), inline=False)
    # thumbnail
    embed.set_thumbnail(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{data['id']}.png")
    await ctx.reply(embed=embed)

# translate text id to english
@bot.command(name='translate', help='Translate text to english')
async def translate(ctx, *, text: str):
    translator = Translator()
    result = translator.translate(text, src='id', dest='en')
    embed=discord.Embed(title="Translation", url="")
    embed.add_field(name="Translated Text", value=result.text, inline=False)
    await ctx.reply(embed=embed)

# send random anime gif
@bot.command(name='animegif', help='Send random anime gif')
async def gif(ctx):
    url = "https://api.tenor.com/v1/random?q=anime&key=LIVDSRZULELA"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    embed=discord.Embed(title="GIF", url="")
    embed.set_image(url=data['results'][0]['media'][0]['gif']['url'])
    await ctx.reply(embed=embed)

# send color
@bot.command(name='randomcolor', help='Send random color')
async def color(ctx):
    embed=discord.Embed(title="", url="")
    embed.set_footer(text="Random Color")
    embed.set_image(url=f"https://dummyimage.com/200x200/{random.randint(0,16777215)}/ffffff.png&text={random.randint(0,16777215)}")
    embed.add_field(name="Color", value=f"#{random.randint(0,16777215):06x}", inline=False)
    await ctx.reply(embed=embed)


#ping and latency
@bot.command(name='ping', help='Ping the bot')
async def ping(ctx):
    
    embed=discord.Embed(title="", url="")
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
    await ctx.reply(embed=embed)


@bot.command(name='woi')
async def respond(ctx):
    if ctx.author.id == 325260673015873548:
        await ctx.send("woi jg")
    else:
        await ctx.send("yem l")

#fun commands
@bot.command(name='roll')
async def roll(ctx, dice: str):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.command(name='say', delete_after=2)
async def say(ctx, *, text: str):
    await ctx.message.delete()
    await ctx.send(text)


#game commands

@bot.command(name='dice')
async def dice(ctx):
    choices = ['1', '2', '3', '4', '5', '6']
    await ctx.send(f'{random.choice(choices)}')

@bot.command(name='batuguntingkertas')
async def rps(ctx, *, choice: str):
    rps = ["batu", "gunting", "kertas"]
    choice = choice.lower()
    if choice in rps:
        bot = random.choice(rps)
        if bot == choice:
            await ctx.send("seri")
        elif bot == "batu" and choice == "gunting":
            await ctx.send("l mng")
        elif bot == "gunting" and choice == "kertas":
            await ctx.send("l mng")
        elif bot == "kertas" and choice == "batu":
            await ctx.send("l mng")
        else:
            await ctx.send("l klh")
    else:
        await ctx.send("slh")

@bot.command(name='anime')
async def anime(ctx, *, anime: str):
    url = "https://api.jikan.moe/v3/search/anime?q=" + anime
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    embed=discord.Embed(title="Anime", url="")
    embed.add_field(name="Title", value=data['results'][0]['title'], inline=False)
    embed.add_field(name="Type", value=data['results'][0]['type'], inline=False)
    embed.add_field(name="Episodes", value=data['results'][0]['episodes'], inline=False)
    embed.add_field(name="Score", value=data['results'][0]['score'], inline=False)
    embed.add_field(name="Synopsis", value=data['results'][0]['synopsis'], inline=False)
    embed.add_field(name="Rated", value=data['results'][0]['rated'], inline=False)
    embed.add_field(name="Link", value=data['results'][0]['url'], inline=False)
    embed.set_thumbnail(url=f"{data['results'][0]['image_url']}")
    await ctx.reply(embed=embed)

# search anime character
@bot.command(name='searchanimechar')
async def character(ctx, *, character: str):
    url = "https://api.jikan.moe/v3/search/character?q=" + character
    async with aiohttp.ClientSession() as session:  
        async with session.get(url) as response:
            data = await response.json()
    embed=discord.Embed(title="Character", url="")
    embed.add_field(name="Name", value=data['results'][0]['name'], inline=False)
    embed.set_image(url=f"{data['results'][0]['image_url']}")
    #if data not found
    if data['results'] == []:
        await ctx.reply("gd")
    else:
        await ctx.reply(embed=embed)

# translate text by emoji


# translate id to spain
@bot.command(name='translateidtoes', help='Translate text to english')
async def translate(ctx, *, text: str):
    translator = Translator()
    result = translator.translate(text, src='id', dest='es')
    embed=discord.Embed()
    embed.add_field(name="Translated Text", value=result.text, inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)

    await ctx.reply(embed=embed)

#calculator
@bot.command(name='calc')
async def calc(ctx, *, equation: str):
    if equation.startswith('-') or equation.startswith('+'):
        await ctx.reply('Please enter a valid equation')
    else:
        try:
            result = eval(equation)
            await ctx.reply(result)
        except Exception:
            await ctx.reply('Please enter a valid equation')

#create invite link
@bot.command(name='invitelink')
async def invite(ctx):
    await ctx.reply(f"https://discord.com/api/oauth2/authorize?client_id=765150186431315987&permissions=8&scope=bot")


@bot.command(name='genshin')
async def character(ctx, *, arg=None):
#  if arg2 == None:  
  if arg == None:
      embeded = discord.Embed(title="Character List")
      for i in cl:
        response = requests.get(char.format(i)).text
        data = json.loads(response)
        embeded.add_field(name=i.title().replace("-", " "), value="{} Star | {}".format(data['rarity'],data['vision']), inline=True)
      await ctx.send(embed=embeded)

  elif arg != None:
      arg = arg.replace(" ", "-").lower()
      if arg in cl:
        response = requests.get(char.format(arg)).text
        data = json.loads(response)
        embeded = discord.Embed(title=data['name'.replace("-", "")],description=data['description'])
        if arg == "traveler-geo":
          embeded.set_thumbnail(url='https://rerollcdn.com/GENSHIN/Characters/Traveler%20(Geo).png')
        elif arg == "traveler-anemo":
          embeded.set_thumbnail(url='https://rerollcdn.com/GENSHIN/Characters/Traveler%20(Anemo).png') 
        else:
          embeded.set_thumbnail(url=imgc.format(data['name'].replace(" ", "%20")))
        embeded.add_field(name="Vision", value=data['vision'], inline=True)
        embeded.add_field(name="Weapon", value=data['weapon'], inline=True)
        rrt = int(data['rarity'])
        strg = "".join([" :star: ".format(x, x*2) for x in range(rrt)])
        embeded.add_field(name="Rarity", value=strg, inline=True)
        for skillTalents in data['skillTalents']:
          embeded.add_field(name="{} : {}".format(skillTalents['unlock'], skillTalents['name']), value=skillTalents['description'].replace("\n\n", "\n"), inline=False)
        for passiveTalents in data['passiveTalents']:
          embeded.add_field(name="Passive Skill: {} \n({})".format(passiveTalents['name'], passiveTalents['unlock']), value=passiveTalents['description'].replace("\n\n", "\n"), inline=True)
        await ctx.send(embed=embeded)
      else:
        await ctx.send("{} not Found!".format(arg).title().replace("-", " "))

@bot.command(name='talent')
async def talent(ctx, *, arg=None):
  if arg == None:
      await ctx.send("Type ?talent CharacterName".format(arg).title().replace("-", " "))

  elif arg != None:
      arg = arg.replace(" ", "-").lower()
      if arg in cl:
        response = requests.get(char.format(arg)).text
        data = json.loads(response)
        embeded = discord.Embed(title=data['name'.replace("-", "")],description=data['description'])
        if arg == "traveler-geo":
          embeded.set_thumbnail(url='https://rerollcdn.com/GENSHIN/Characters/Traveler%20(Geo).png')
        elif arg == "traveler-anemo":
          embeded.set_thumbnail(url='https://rerollcdn.com/GENSHIN/Characters/Traveler%20(Anemo).png') 
        else:
          embeded.set_thumbnail(url=imgc.format(data['name'])) 
        embeded.add_field(name="Vision", value=data['vision'], inline=True)
        embeded.add_field(name="Weapon", value=data['weapon'], inline=True)
        rrt = int(data['rarity'])
        strg = "".join([" :star: ".format(x, x*2) for x in range(rrt)])
        embeded.add_field(name="Rarity", value=strg, inline=True)
        for skillTalents in data['skillTalents']:
          embeded.add_field(name="{} : {}".format(skillTalents['unlock'], skillTalents['name']), value=skillTalents['description'].replace("\n\n", "\n"), inline=False)
          for upgrades in skillTalents['upgrades']:
            embeded.add_field(name="{}".format(upgrades['name']), value=upgrades['value'], inline=True)
        # for passiveTalents in data['passiveTalents']:
        #   embeded.add_field(name="Passive Skill: {} \n({})".format(passiveTalents['name'], passiveTalents['unlock']), value=passiveTalents['description'].replace("\n\n", "\n"), inline=True)

        await ctx.send(embed=embeded)
      else:
        await ctx.send("{} not Found!".format(arg).title().replace("-", " "))

@bot.command(name='typechar')
async def cons(ctx, *, arg=None):
  if arg == None:
      await ctx.send("Type the Character!".format(arg).title())

  elif arg != None:
      arg = arg.replace(" ", "-").lower()
      if arg in cl:
        response = requests.get(char.format(arg)).text
        data = json.loads(response)
        embeded = discord.Embed(title=data['name'.replace("-", "")],description=data['description'])
        if arg == "traveler-geo":
          embeded.set_thumbnail(url='https://rerollcdn.com/GENSHIN/Characters/Traveler%20(Geo).png')
        elif arg == "traveler-anemo":
          embeded.set_thumbnail(url='https://rerollcdn.com/GENSHIN/Characters/Traveler%20(Anemo).png') 
        else:
          embeded.set_thumbnail(url=imgc.format(data['name'])) 
        embeded.add_field(name="Vision", value=data['vision'], inline=True)
        embeded.add_field(name="Weapon", value=data['weapon'], inline=True)
        rrt = int(data['rarity'])
        strg = "".join([" :star: ".format(x, x*2) for x in range(rrt)])
        embeded.add_field(name="Rarity", value=strg, inline=True)
        for i in range(6) :
          embeded.add_field(name=data['constellations'][i]['unlock'], value="{} \n {}".format(data['constellations'][i]['name'], data['constellations'][i]['description']), inline=True)

        await ctx.send(embed=embeded)
      else:
        await ctx.send("{} not Found!".format(arg).title().replace("-", " "))

@bot.command(name='artifact')
async def artifact(ctx, *, arg=None): 
    if arg == None:
      def listToString(wl):  
        str1 = "\n" 
        return (str1.join(wl))  
      artlist = requests.get('https://api.genshin.dev/artifacts').text
      al = json.loads(artlist) 
      embeded = discord.Embed(title="Artifact List", description=listToString(al).title().replace("-", " "))
      await ctx.send(embed=embeded)

     ## # Use this if you wanted to show List and Showing some info
     ## # Not recommended because load to many data
      # embeded = discord.Embed(title="Artifact List")
      # artlist = requests.get('https://api.genshin.dev/artifacts').text
      # al = json.loads(artlist)
      # for i in al:
      #   response = requests.get(art.format(i)).text
      #   data = json.loads(response)
      #   embeded.add_field(name=i.title().replace("-", " "), value="2P: {}\n4P: {}".format(data['2-piece_bonus'], data['4-piece_bonus']), inline=True)
      # await ctx.send(embed=embeded)

    elif arg != None:
      arg = arg.replace(" ", "-").lower()
      artlist = requests.get('https://api.genshin.dev/artifacts').text
      al = json.loads(artlist)
      if arg in al:
        response = requests.get(art.format(arg)).text
        data = json.loads(response)
        embeded = discord.Embed(title=data['name'])
        embeded.set_thumbnail(url=imga.format(data['name'].lower().replace(" ", "_")))
        rrt = int(data['max_rarity'])
        strg = "".join([" :star: ".format(x, x*2) for x in range(rrt)])
        embeded.add_field(name="Max Rarity", value=strg, inline=True) 
        embeded.add_field(name="2 Pieces", value=data['2-piece_bonus'], inline=False)
        embeded.add_field(name="4 Pieces", value=data['4-piece_bonus'], inline=False)
        await ctx.send(embed=embeded)
      else:
        await ctx.send("{} not Found!".format(arg).title().replace("-", " "))

@bot.command(name='weapon')
async def weapon(ctx, *, arg=None): 
    if arg == None:
      def listToString(wl):  
        str1 = "\n" 
        return (str1.join(wl))  
      wplist = requests.get('https://api.genshin.dev/weapons').text
      wl = json.loads(wplist)  
      embeded = discord.Embed(title="Weapon List", description=listToString(wl).title().replace("-", " "))
      await ctx.send(embed=embeded)

      ## # Same as artifact, but Weapons hold to many data, so it only shown a part of it
      # for i in wl:
      #   response = requests.get(wp.format(i)).text
      #   data = json.loads(response)
      #   embeded.add_field(name=i.title().replace("-", " "), value="Type: {}".format(data['type']), inline=True)
      # await ctx.send(embed=embeded)

    elif arg != None:
      arg = arg.replace(" ", "-").lower()
      wplist = requests.get('https://api.genshin.dev/weapons').text
      wl = json.loads(wplist)  
      if arg in wl:
        response = requests.get(wp.format(arg)).text
        data = json.loads(response)
        embeded = discord.Embed(title=data['name'])
        print(data['name'])
        embeded.set_thumbnail(url=imgw.format(data['name'].replace(" ", "_")))
        embeded.add_field(name="Type", value=data['type'], inline=True)
        embeded.add_field(name="Base ATK", value=data['baseAttack'], inline=True) 
        rrt = int(data['rarity'])
        strg = "".join([" :star: ".format(x, x*2) for x in range(rrt)])
        embeded.add_field(name="Rarity", value=strg, inline=True)
        embeded.add_field(name="Sub Stat", value=data['subStat'], inline=True)
        embeded.add_field(name="Where to Get", value=data['location'], inline=True)
        embeded.add_field(name="Passive: {}".format(data['passiveName']), value=data['passiveDesc'], inline=False)
        await ctx.send(embed=embeded)
      else:
        await ctx.send("{} not Found!".format(arg).title().replace("-", " "))

#pretty embed for help
@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed()
    # set author
    embed.set_author(name=bot.user.name + ' • Help', url="", icon_url = bot.user.avatar_url)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.add_field(name = '__**🔧 Mods**__', value= "`ping`, `info`, `userinfo` <user>, `servericon`, `avatar`", inline = False)
    embed.add_field(name = '__**😋 Fun**__', value = "`pokemon` <name>, `animegif`, `flip` <user>, `grey` <user>, `meme`, ", inline = False)
    embed.add_field(name = '__**⚙️ Utilities**__', value = "`weater` <city>, `randomcolor`, `translate` <text>, `translatetoes <text>`, `quote`, `today`, `movie`, `trendingmovie`, `wiki` <text>, `covid`, `anime` <anime>, `calc`, `searchanimechar <char anime>`", inline = False)
    
    embed.add_field(name = '__**🎮 Online Games**__', value = "`genshin` <char>, `weapon` <name>, `typechar` <char>, `artifact` <name>, `talent` <char>", inline = False)
    # embed.add_field(name = 'Champion', value = "Something", inline = True)
    # embed.add_field(name = 'Rank', value = "Something", inline = True)
    timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y") + " " + datetime.datetime.utcnow().strftime("%H:%M:%S")
    embed.set_footer(text=f'Requested by {ctx.author.name} • {timestamp}', icon_url=ctx.author.avatar_url)

    #else:
    #  embed.set_footer(text=time.strftime("%d/%m/%Y") + " | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%A"))
    await ctx.send(embed=embed)




@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

bot.run(TOKEN)