# Импортированные библиотеки
import discord
import time
import threading
import sys
import configparser
from discord.ext import commands

Config = configparser.ConfigParser()
Config.read('config.ini')

# Получаем токен из конфигурации
TOKEN = str(Config['Discord']['BOT_TOKEN'])

# Установка бота
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
bot.remove_command('help')  # Удаление дефолтной команды help

# Группы
others = bot.create_group("сведения", "узнайте побольше!")

# Время из секундомера
updated_time = ''

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

# Команда, которая отвечает на вызов пользователя и дает список основных команд для интерактирования с ботом
@others.command(description = "Отправляет список команд вам в личные сообщения.")
async def help(ctx):
    help_embed = discord.Embed(title="Здравствуйте!", description="", color=0x0FF00)
    help_embed.add_field(name="Вот список основных команд для интерактирования со мной:", value="\n".join([str(i+1)+". "+x.name for i, x in enumerate(bot.commands)]), inline=False)
    help_embed.add_field(name="П.С:", value="Напишите `/help <команду>` для подсказки на правильное использование команды", inline=False)
    await ctx.author.send(embed = help_embed)
    await ctx.respond(content = 'Отправил вам список команд в личных сообщениях, изучите их, пожалуйста!')
    
# Команда, отправляющая сообщение в чат со сведением о боте
@others.command(description = "Отправляет небольшое сведение обо мне.")
async def information(ctx):
    ping_out = str((round(bot.latency * 1000))) + ' мс'
    current_time = str(updated_time)

    some_embed = discord.Embed(title="Мои сведения:", description="", color=0x0FF00)
    some_embed.add_field(name='Характеристика:', value='Я - бот, написанный на библиотеке Py-Cord (https://pycord.dev/) на Python с версии 3.12.00')
    some_embed.add_field(name='Производительность:', value='Задерживаюсь на ' + ping_out + '\n' + 'Работаю уже ' + current_time + '!')

    await ctx.respond(embed = some_embed)

# Обработчик сообщений
@bot.event
async def on_message(message):
    await bot.process_commands(message)

# Установка потока секундомера
stopwatch_thread = threading.Thread(target=start_stopwatch)
stopwatch_thread.daemon = True
stopwatch_thread.start()

# Запуск бота
bot.run(TOKEN)
