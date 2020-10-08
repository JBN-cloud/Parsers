from telebot import TeleBot
import telebot
import constants
from bs4 import BeautifulSoup
import requests
import os
from sql import SQLighter
from aiogram import Bot, types, Dispatcher, executor


bot: TeleBot = telebot.TeleBot(constants.token)
bot.remove_webhook()
secbot = Bot(token=constants.token)
dp = Dispatcher(secbot)
global flagsearch
global flagartist
flagsearch = False
flagartist = False

db = SQLighter('db.db')

@bot.message_handler(commands=['start'])
def handle_start(message):
    global flagsearch
    global flagartist
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row('/start', '/toclose')
    user_markup.row('/search', '/help', 'last 10 audios')
    user_markup.row('/subscribe', '/unsubscribe')
    bot.send_message(message.from_user.id, 'Welcome! Choose something.', reply_markup=user_markup)
    flagsearch = False
    flagartist = False

@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if (not db.subscriber_exists(message.from_user.id)):
        db.add_subscriber(message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True)

    await message.answer("Вы успешно подписались на рассылку!")


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if (not db.subscriber_exists(message.from_user.id)):
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны.")
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.")

@bot.message_handler(commands=['toclose'])
def handle_start(message):
    hide_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, "Have a nice day!)", reply_markup=hide_markup)


@bot.message_handler(commands=['help'])
def handle_start(message):
    bot.send_message(message.from_user.id, "start - начать взаимодействие с ботом\nhelp - посмотреть возможности бота\nclose - закрыть бота\nsearch - начать поиск музыки\nsubscribe - подписаться на рассылку\nunsubscribe - отписаться от рассылки")


@bot.message_handler(commands=['search'])
def search_text(message):
    global flagsearch
    global flagartist
    flagsearch = True
    flagartist = True
    bot.send_message(message.chat.id, 'Enter names of artist and track separated by a space. For example "30 seconds to mars save me"')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    global flagsearch, flagartist
    directory = 'D:/Music/qq'
    times = 0
    if message.text == 'last 10 audios':
        all_files_in_directory = os.listdir(directory)
        for file in all_files_in_directory:
            times += 1
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_audio = telebot.types.InlineKeyboardButton(file, callback_data=file)
            keyboard.add(key_audio)
            bot.send_message(message.from_user.id, '🔈🔈🔈🔈', reply_markup=keyboard)

            if (times == 10):
                exit()

    if (flagsearch & flagartist):

        def get_html(url):
            r = requests.get(url)
            return r.text

        artist = message.text.lower()
        lst = artist.replace('.', '').split()
        urlartist = "https://zaycev.net/search.html?query_search="
        for words in lst:
            urlartist += words + "+"
        urlartist = 'https://www.fonbet.ru/bets/'

        html_page = get_html(urlartist)
        soup = BeautifulSoup(html_page, "html.parser")
        print(soup)
        try:
            items = 'https://zaycev.net' + soup.find('a', class_='musicset-track__download-link').get('href') + '?spa=false'
        except AttributeError:
            bot.send_message(message.chat.id, 'К сожалению такого трека не существует или его нельзя скачать')
            bot.send_message(message.chat.id, 'Повторите попытку нажав /search')
            exit()

        r = requests.get(items)

        with open(directory + '/' + artist + '.mp3', 'wb') as f:
            f.write(r.content)

        audio = open(directory + '/' + artist + '.mp3', 'rb')
        bot.send_chat_action(message.from_user.id, 'upload_audio')
        bot.send_audio(message.chat.id, audio)
        audio.close()
        flagartist = False


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    directory = 'D:/Music/qq'
    all_files_in_directory = os.listdir(directory)
    for file in all_files_in_directory:
        if call.data == file:
            audio = open(directory + '/' + file, 'rb')
            bot.send_audio(call.message.chat.id, audio)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="downloaded✅")


if __name__ == "__main__":
    while(1):
        bot.polling(none_stop=True)
        executor.start_polling(dp, skip_updates=False)



