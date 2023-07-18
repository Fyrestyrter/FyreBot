import json
import random
import discord
import os
import youtube_dl
from discord.ext import commands
from dotenv import load_dotenv
from dateutil import tz

load_dotenv()
TOKEN = os.getenv("TOKEN")
MESSAGE_ID = os.getenv("MESSAGE_ID")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix='>', intents=intents)

hello_words = ["hello", "hi", "привет", "как дела"]
info_words = ["как сделать", "куда обратиться", "помощь", "помогите", "позвонить", "написать ", "поддержка", "support"]
bye_words = ["пока", "досвидания", "bye"]

REACTION_ROLE_MAP = {
    '👎': 'Пахан',  # Замените '👎' на нужную реакцию и 'Роль1' на нужное имя роли
    '👍': 'Алкашня',  # Замените '👍' на нужную реакцию и 'Роль2' на нужное имя роли
}

user_timezone = tz.tzlocal()


@bot.event
async def on_ready():
    print('I am Ready!')


@bot.event
async def on_member_join(member):
    # Создаем словарь с информацией о новом пользователе
    user_info = {
        'username': member.name,
        'display_name': member.display_name,
        'id': member.id,
        'joined_at': member.joined_at.astimezone(user_timezone).strftime("%d-%m-%Y %H:%M:%S"),
        'created_at': member.created_at.astimezone(user_timezone).strftime("%d-%m-%Y %H:%M:%S")
    }

    if not os.path.isfile('user_info.json'):
        with open('user_info.json', 'w') as file:
            json.dump({}, file)

    # Открываем JSON файл для записи информации
    with open('user_info.json', 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = {}

    # Добавляем информацию о новом пользователе в словарь
    data[str(member.name)] = user_info

    # Записываем обновленные данные в JSON файл
    with open('user_info.json', 'w') as file:
        json.dump(data, file, indent=4)

    @bot.event
    async def on_member_update(before, after):
        if not os.path.isfile('user_info.json'):
            return

        with open('user_info.json', 'r') as file:
            data = json.load(file)

        if str(after.id) in data:
            data[str(after.id)]['display_name'] = after.display_name

            with open('user_info.json', 'w') as file:
                json.dump(data, file, indent=4)


@bot.event
async def on_member_remove(member):
    if not os.path.isfile('user_info.json'):
        return

    with open('user_info.json', 'r') as file:
        data = json.load(file)

    # Удаляем информацию о вышедшем пользователе из словаря
    if str(member.id) in data:
        del data[str(member.id)]

    if str(member.name) in data:
        del data[str(member.name)]

    with open('user_info.json', 'w') as file:
        json.dump(data, file, indent=4)


@bot.event
async def on_raw_reaction_add(payload):
    # Проверяем, что реакция добавлена на нужное сообщение
    if payload.message_id == int(MESSAGE_ID):
        # Получаем объект сервера
        guild = bot.get_guild(payload.guild_id)

        # Получаем объект пользователя
        user = guild.get_member(payload.user_id)

        # Получаем роль, соответствующую реакции
        role_name = REACTION_ROLE_MAP.get(payload.emoji.name)

        # Выдача роли пользователю
        if role_name and user:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await user.add_roles(role)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    msg = message.content.lower()
    msg_list = msg.split()

    # if (msg in hello_words) or len(list(set(msg_list + hello_words)))<len(msg_list) + len(hello_words):
    find_hello_words = False
    for item in hello_words:
        if msg.find(item) >= 0:
            find_hello_words = True
    if (find_hello_words):
        await message.channel.send('Привет, чего изволите?')

    find_words = False
    for item in bye_words:
        if msg.find(item) >= 0:
            find_words = True
    if (find_words):
        await message.channel.send('Пока!')

    # if (msg in info_words) or len(list(set(msg_list + info_words)))<len(msg_list) + len(info_words):
    find_info_words = False
    for item in info_words:
        if msg.find(item) >= 0:
            find_info_words = True
    if (find_info_words):
        await message.channel.send('Спасибо за обращение, ваш вопрос передан специалисту! Ожидайте!')


@bot.command()
async def meme(ctx):
    joke = [
        "https://imgur.com/t/pepe/qjxtX9W",
        "https://imgur.com/t/pepe/Wkrvc7Z",
        "https://imgur.com/gallery/4GUOjyS",
        "https://imgur.com/gallery/nkQ9Etq"
    ]
    r_joke = random.choice(joke)
    await ctx.send(r_joke)


@bot.command()
async def pepe(ctx):
    await ctx.send(" https://i.imgur.com/Hab3RJO.jpg ")


@bot.command()
async def add_user(ctx, nickname: str):
    # Проверяем, существует ли пользователь с указанным никнеймом на сервере
    member = discord.utils.find(lambda m: m.name == nickname or m.display_name == nickname, ctx.guild.members)
    if not member:
        await ctx.send(f'Пользователь с никнеймом {nickname} не найден на сервере.')
        return
    # Создаем словарь с информацией о новом пользователе
    user_info = {
        'username': member.name,
        'display_name': member.display_name,
        'id': member.id,
        'joined_at': member.joined_at.astimezone(user_timezone).strftime("%d-%m-%Y %H:%M:%S"),
        'created_at': member.created_at.astimezone(user_timezone).strftime("%d-%m-%Y %H:%M:%S")
    }

    # Открываем JSON файл для загрузки информации
    with open('user_info.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Проверяем, нет ли уже информации о пользователе в словаре
    if nickname in data:
        await ctx.send(f'Информация о пользователе {nickname} уже существует.')
        return
    # if member.display_name in user_info['display_name']:
    #     await ctx.send(f'Информация о пользователе {nickname} уже существует.')
    #     return

    # Добавляем информацию о новом пользователе в словарь
    data[nickname] = user_info

    # Записываем обновленные данные в JSON файл
    with open('user_info.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    await ctx.send(f'Информация о пользователе {nickname} успешно добавлена в JSON файл.')


@bot.command()
async def play(ctx, url: str):
    # Проверяем, находится ли бот в голосовом канале
    if ctx.voice_client is None:
        # Проверяем, есть ли пользователь в голосовом канале
        if ctx.author.voice:
            # Подключаемся к голосовому каналу пользователя
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send('Вы должны находиться в голосовом канале, чтобы я мог проигрывать музыку.')
            return

    # Создаем объект YouTubeDL для загрузки аудио из видео YouTube
    ydl_opts = {'format': 'worstaudio/best',
                              'noplaylist': 'True', 'simulate': 'True', 'preferredquality': '192',
                              'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']

    # Получаем голосовой канал бота
    voice_channel = ctx.voice_client

    # Проигрываем аудио в голосовом канале
    voice_channel.stop()
    voice_channel.play(discord.FFmpegPC>MAudio(url2), after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send(f'Проигрывается музыка: {url}')


@bot.command()
async def leave(ctx):
    # Проверяем, находится ли бот в голосовом канале
    if ctx.voice_client is not None:
        # Отключаем бота от голосового канала
        await ctx.voice_client.disconnect()
        await ctx.send('Бот покинул голосовой канал.')
    else:
        await ctx.send('Бот не находится в голосовом канале.')


bot.run(TOKEN)

# Документируйте ваш код, включая описание команд, формат записи данных в JSON файл и примеры работы бота, в виде файла README.md
