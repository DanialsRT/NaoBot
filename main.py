# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from config import token

from youtube_dl import YoutubeDL
from asyncio import sleep

bot = commands.Bot(command_prefix='n!')


@bot.event
async def on_ready():
    print('Bot online!')


server, server_id, name_channel = None, None, None

domains = ['https://www.youtube.com/', 'https://youtube.com/', 'http://www.youtube.com/', 'https://youtu.be/',
           'http://youtu.be/', 'https://music.youtube.com/', 'http://music.youtube.com/']


async def check_domains(link):
    for x in domains:
        if link.startswith(x):
            return True
    return False


@bot.command()
async def play(ctx, arg):
    """Воспроизводит музыку по ссылке"""
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
        if not await check_domains(URL):
            vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\bin\\ffmpeg.exe", source=URL, **FFMPEG_OPTIONS))

            while vc.is_playing():
                await sleep(1)
            if not vc.is_paused():
                await vc.disconnect()
        else:
            await ctx.send(f'{ctx.message.author.mention}, ссылка не корректна.')


@bot.command()
async def leave(ctx):
    """Команда покинуть комнату"""
    try:
        await ctx.voice_client.disconnect()
    except:
        await ctx.channel.send(f'{ctx.author.mention}, бот уже покинул комнату')


@bot.command()
async def pause(ctx):
    """Пауза трека"""
    try:
        voice_channel = ctx.message.author.voice.channel
        if not vc.is_paused():
            vc.pause()
            await ctx.channel.send(f'{ctx.author.mention}, музыка на паузе!')
        else:
            await ctx.channel.send(f'{ctx.author.mention}, музыка не воспроизводится!')
    except:
        print('Error')


@bot.command()
async def resume(ctx):
    """Продолжить трек"""
    try:
        if vc.is_paused():
            vc.resume()
            await ctx.channel.send(f'{ctx.author.mention}, музыка продолжилась!')
        else:
            await ctx.channel.send(f'{ctx.author.mention}, музыка уже воспроизводится!')
    except:
        print('Error')

@bot.command()
async def stop(ctx):
    """Прекращает воспроизведение трека"""
    if vc.is_playing():
        vc.stop()
        await ctx.channel.send('Всем пока!')
        await ctx.voice_client.disconnect()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, музыка не воспроизводится!')


bot.run(token)
