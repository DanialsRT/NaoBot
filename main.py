# -*- coding: utf-8 -*-

import pafy
from discord import FFmpegPCMAudio, PCMVolumeTransformer

import discord, youtube_dl, os, asyncio, time
from discord.ext import commands
from config import token

from youtube_dl import YoutubeDL
from asyncio import sleep

bot = commands.Bot(command_prefix='n!')

@bot.event
async def on_ready():
    print('Bot online!')

server, server_id, name_channel = None, None, None

domains = ['https://www.youtube.com/', 'https://youtube.com/', 'http://www.youtube.com/', 'https://youtu.be/', 'http://youtu.be/', 'https://music.youtube.com/', 'http://music.youtube.com/']

async def check_domains(link):
    for x in domains:
        if link.startswith(x):
            return True
    return False

@bot.command()
async def p(ctx, arg):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'False'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    global vc

    try:
        voice_channel = ctx.message.author.voice.channel
        vc = await voice_channel.connect()
    except:
        print('Уже подключен или не удалось подключиться')

    if vc.is_playing():
        await ctx.send(f'{ctx.message.author.mention}, музыка уже проигрывается.')

    else:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(arg, download=False)

        URL = info['formats'][0]['url']

        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\bin\\ffmpeg.exe", source=URL, **FFMPEG_OPTIONS))

        while vc.is_playing():
            await sleep(1)
        if not vc.is_paused():
            await vc.disconnect()

@bot.command()
async def play(ctx, *, command = None):
    """Воспроизводит музыку"""
    global server, server_id, name_channel
    author = ctx.author
    if command == None:
        server = ctx.guild
        name_channel = ctx.author.voice.channel.name
        voice_channel = discord.utils.get(server.voice_channels, name = name_channel)
    params = command.split(' ')
    if len(params) == 1:
        source = params[0]
        server = ctx.guild
        name_channel = ctx.author.voice.channel.name
        voice_channel = discord.utils.get(server.voice_channels, name = name_channel)
        print('param 1')
    elif len(params) == 3:
        server_id = params[8]
        voice_id = params[1]
        source = params[2]
        try:
            server_id = int(server_id)
            voice_id = int(voice_id)
        except:
            await ctx.channel.send(f'{author.mention}, id сервера или войса должно быть целочисленным!')
            return
        server = bot.get_guild(server_id)
        voice_channel = discord.utils.get(server.voice_channels, id='voice_id')
    else:
        await ctx.channel.send(f'{author.mention} команда не корректна')

    voice = discord.utils.get(bot.voice_clients, guild = server)
    if voice is None:
        await voice_channel.connect()
        voice = discord.utils.get(bot.voice_clients, guild = server)

    if source == None:
        pass

    elif source.startswith('http'):
        if not await check_domains(source):
            await ctx.channel.send(f'{author.mention}, ссылка не является разрешенной')
            return

        song_there = os.path.isfile('song.mp3')
        try:
            if song_there:
                os.remove('song.mp3')
        except PermissionError:
            await ctx.channel.send('Недостаточно прав для удаления файла!')
            return
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([source])
        for file in os.listdir('./'):
            if file.endswith('.mp3'):
                os.rename(file, 'song.mp3')
                #print('1')
        for file in os.listdir('./'):
            if file.endswith('.mp3'):
                voice.play(discord.FFmpegPCMAudio(file))
                #print('1')
    else:
        voice.play(discord.FFmpegPCMAudio(f'./{source}'))

@bot.command()
async def leave(ctx):
    """Команда покинуть комнату"""
    global server, name_channel
    voice = discord.utils.get(bot.voice_clients, guild=server)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, бот уже покинул комнату')

@bot.command()
async def pause(ctx):
    """Пауза трека"""
    voice = discord.utils.get(bot.voice_clients, guild=server)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, музыка не воспроизводится!')

@bot.command()
async def resume(ctx):
    """Продолжить трек"""
    voice = discord.utils.get(bot.voice_clients, guild=server)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, музыка уже воспроизводится!')

@bot.command()
async def stop(ctx):
    """Прекращает воспроизведение трека"""
    voice = discord.utils.get(bot.voice_clients, guild=server)
    if voice.is_playing():
        voice.stop()
        await ctx.channel.send('Всем пока!')
        await ctx.voice_client.disconnect()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, музыка не воспроизводится!')


bot.run(token)