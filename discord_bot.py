# Импортированные библиотеки
import discord
import time
import threading
import sys
import re
import ctypes
import configparser
import random
import json
import requests
import asyncio
from translate import Translator
from discord.ext import commands

# Установка парсера для конфига
Config = configparser.ConfigParser()
Config.read('config.ini')

# Получения токена из конфига
TOKEN = Config['Discord']['BOT_TOKEN']

# Установка стандартного префикса
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.remove_command('help')  # Удаление дефолтной команды help

# Задайте новый заголовок для консоли
new_title = "Running code for Discord Bot: MUGEN"
ctypes.windll.kernel32.SetConsoleTitleW(new_title)

allowed_characters = "_!$%^&*?\|~"

# Группы
others = bot.create_group("сведения", "узнайте побольше!")

# Время для дисплея
updated_time = ''

# Проверка символов для смены префикса
def contains_special_char(string):
    pattern = re.compile(allowed_characters)
    if pattern.search(string) is None:
        return False
    else:
        return True

# Перевод на русский
def translate_question(question):
    translator = Translator()
    translated_question = translator.translate(question, dest='ru').text
    return translated_question

# Функция для запуска секундомера
def start_stopwatch():
    global updated_time

    seconds = 0
    minutes = 0
    hours = 0

    while True:
        time_string = f"{hours:02}:{minutes:02}:{seconds:02}"

        updated_time = time_string

        sys.stdout.write("\rВремя текущей сессии: " + time_string)
        sys.stdout.flush()

        seconds += 1
        if seconds == 60:
            seconds = 0
            minutes += 1
        if minutes == 60:
            minutes = 0
            hours += 1

        time.sleep(1)

# Смена префикса
@bot.command(name='change_prefix')
async def change_prefix(ctx, new_prefix=None):
    allowed_chars = 'Вот список разрешённых символов: ' + '`' + allowed_characters + '`'

    if not contains_special_char(new_prefix):
        await ctx.send('Новый префикс должен состоять только из символа.\nЕсли только из букв или цифр - я вас бы не понимал!\n\n' + allowed_chars)
        return
    confirmation_embed = discord.Embed(title='Подтверждение', description=f'Вы уверены, что хотите изменить префикс на "{new_prefix}"?')
    confirmation_embed.set_footer(text='Нажмите на реакцию, чтобы подтвердить действие. В противном случае через 15 секунд - подтверждение закончится.')
    confirmation_message = await ctx.message.reply(embed=confirmation_embed)
    await confirmation_message.add_reaction('✅')
    await confirmation_message.add_reaction('❌')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message == confirmation_message

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=15.0, check=check)
    except:
        await confirmation_message.delete()
        await ctx.send('Время ожидания истекло, автобус уехал!')
        return

    if user and str(reaction.emoji) == '❌':
        await confirmation_message.delete()
        await ctx.send('Действие отменено, а ведь мы были так близки.')
        return

    bot.command_prefix = new_prefix
    await confirmation_message.delete()
    await ctx.send(f'Префикс команд изменен на "{new_prefix}"! Теперь мы можем понимать друг друга!')

# Помощь по командам
@bot.command(name='help')
async def help(ctx):
    help_embed = discord.Embed(title="Здравствуйте!", description="", color=0x0FF00)
    help_embed.add_field(name="Вот список основных команд для интерактирования со мной:", value="\n".join([str(i+1)+". "+x.name for i, x in enumerate(bot.commands)]), inline=False)
    help_embed.add_field(name="П.С:", value="Напишите `/help <команду>` для подсказки на правильное использование команды", inline=False)
    await ctx.author.send(embed = help_embed)
    await ctx.message.reply(content = 'Отправил вам список команд в личных сообщениях, изучите их, пожалуйста!')

# Информация
@bot.command(name = "info")
async def information(ctx):
    ping_out = str((round(bot.latency * 1000))) + ' мс'
    current_time = str(updated_time)

    some_embed = discord.Embed(title="Мои сведения:", description="", color=0x0FF00)
    some_embed.add_field(name='Характеристика:', value='Я - бот, созданный пользователем <@416609918221811732> с поддержкой контрибьютора <@898973009484873748>, написанный на библиотеке Py-Cord (https://pycord.dev/) на Python с версии 3.12.00')
    some_embed.add_field(name='Производительность:', value='Задерживаюсь на ' + ping_out + '\n' + 'Работаю уже ' + current_time + '!')
    some_embed.add_field(name='\nВ чём заключается моя работа?', value='Я, как бот, обязан предоставлять пользователям Discord удобство в использование мессенджера!\nЯ могу облегчить работу администраторов, модераторов и других должностных лиц, обязанные следить за порядком сервера.\nЯ могу развлекать пользователей, чтобы предоставить им комфортное времяпровождение за Discord.', inline=False)
    some_embed.add_field(name='\nМогу ли я как-то поддержать вас?', value='На данный момент, я не принимаю пожертвования для усиления самого себя.\nЭто слишком ответственная для меня работа, поэтому, я начинаю только с самого низу.\nОднако, я не всегда работаю, но я задумаюсь о пожертвовании.', inline=False)
    some_embed.add_field(name='\nВы открыты для использования?', value='Да! Вы можете узнать обо мне по-больше с помощью [данной репозитории GitHub](https://github.com/amogus-jpg/MUGEN-PyCord)!\nНо, когда вы будете делать бота с использованием моего исходного кода, указывайте пользователя <@416609918221811732> как автора, следуя по лицензии.\nПо желанию, вы можете также указать контрибьютора <@898973009484873748>.')

    await ctx.message.reply(embed = some_embed)

# Камень, ножницы, бумага
@bot.command(name="rps")
async def rock_paper_scissors(ctx, choice):
    allowed_items = ["камень", "ножницы", "бумага"]
    bot_choice = random.choice(allowed_items)

    # Приводим выбор пользователя к нижнему регистру
    choice = choice.lower()
    display_choice = str(str.capitalize(choice))

    if choice in allowed_items:
        await ctx.message.reply(f"Твой выбор: {display_choice}\nМой выбор: {str.capitalize(bot_choice)}")
        await determine_winner(ctx, choice, bot_choice)
    else:
        await ctx.message.reply("Можно выбрать только камень, ножницы или бумагу!\n\nНикаких выдуманных правил!")

async def determine_winner(ctx, player_choice, bot_choice):
    player_choice = player_choice.lower()

    if player_choice == bot_choice:
        await ctx.message.reply("Ничья!")
    elif (
        (player_choice == "камень" and bot_choice == "ножницы")
        or (player_choice == "ножницы" and bot_choice == "бумага")
        or (player_choice == "бумага" and bot_choice == "камень")
    ):
        win_give = ["Прошу вас, взять свою удачную удачи в руки! :four_leaf_clover:", "Полагаю, вы заслуживаете вашу вкусную награду! :hamburger:", "Вы настолько везучи, что получаете самую яркую звезду из космоса! :star2:", "Отличная игра! Но, вы забыли взять свой сладкий сюрприз! :bubble_tea:"]
        await ctx.message.reply(f"Ты выиграл!\n{random.choice(win_give)}")
    else:
        await ctx.message.reply("Я выиграл!\nНе расстраивайся, шансы здесь случайны, поэтому, не стоит разочаровываться!")

# Викторина
@bot.command(name='quiz')
async def trivia(ctx):
    # Запрос вопроса от Open Trivia Database
    response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
    data = json.loads(response.text)
    question_data = data["results"][0]

    # Перевод вопроса и ответов на русский с использованием библиотеки translate
    translator = Translator(to_lang='ru')
    
    translated_question = translator.translate(question_data["question"])
    translated_answers = [translator.translate(ans) for ans in question_data["incorrect_answers"]]
    translated_answers.append(translator.translate(question_data["correct_answer"]))

    # Формирование строки с вариантами ответов
    answers_string = "\n".join([f"{index + 1}. {answer}" for index, answer in enumerate(translated_answers)])

    # Отправляем вопрос и варианты ответов в канал
    question_embed = discord.Embed(title="Викторина", description=translated_question, color=0x00ff00)
    question_embed.add_field(name="Варианты ответов", value=answers_string, inline=False)
    question_embed.add_field(name="Успейте ответить через минуту!", value='', inline=False)
    await ctx.message.reply(embed=question_embed)

    # Ожидаем ответ от пользователя
    def check(answer):
        return answer.author == ctx.message.author and answer.channel == ctx.message.channel

    try:
        user_answer = await bot.wait_for('message', check=check, timeout=60)
    except asyncio.TimeoutError:
        await ctx.message.reply(f"Не успели выбрать ответ, а вот и он - {str.capitalize(translator.translate(question_data['correct_answer']))}")
        return

    # Проверяем ответ
    translated_user_answer = translator.translate(user_answer.content)
    correct_answers = [translator.translate(ans) for ans in question_data['incorrect_answers']]
    correct_answers.append(translator.translate(question_data['correct_answer']))

    if translated_user_answer.lower() in [ans.lower() for ans in correct_answers]:
        await ctx.message.reply(f"Превосходно!\nОтвет - {str.capitalize(translator.translate(question_data['correct_answer']))}")
    else:
        await ctx.message.reply(f"Увы, но это неправильно!\nПравильный ответ - {str.capitalize(translator.translate(question_data['correct_answer']))}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

stopwatch_thread = threading.Thread(target=start_stopwatch)
stopwatch_thread.daemon = True
stopwatch_thread.start()

bot.run(str(TOKEN))
