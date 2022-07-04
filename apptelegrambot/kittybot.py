import logging
import os
import sys
from datetime import datetime as dt

import datetime

from random import randint

from dotenv import load_dotenv

import requests
from logging import StreamHandler
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


load_dotenv()

secret_token = os.getenv('TOKEN')

URL = 'https://api.thecatapi.com/v1/images/search'
URL_IP = 'http://ip-api.com/json'

logging.basicConfig(
    level=logging.DEBUG,
    filename='../kitty_bot.log',
    encoding='utf-8',
    format='%(asctime)s, %(levelname)s, %(funcName)s, %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(funcName)s - %(levelname)s - %(message)s - %(lineno)s '
)
handler.setFormatter(formatter)


def get_new_image():
    """Получает от API картинку кота."""
    try:
        response = requests.get(URL)
    except Exception as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)
    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def get_ip():
    """Получает от API IP-пользователя."""
    try:
        response = requests.get(URL_IP).json()
    except Exception as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')
        return 'Сервер не доступен'
    show_ip = response.get('query')
    return f'Ваш IP-adress - {show_ip}'


def random_number():
    """Получает рандомное число от 0 до 100."""
    digit = randint(0, 100)
    return f'Вам выпало число - {digit}'


def new_cat(update, context):
    """Команда для показа нового фото кота."""
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())


def date_now(update, context):
    """Команда которая показывает текущее время."""
    chat = update.effective_chat
    # local = dt.now(tzlocal()).tzname()
    delta = datetime.timedelta(hours=3, minutes=0)
    msk = dt.now() + delta
    is_date_msk = msk.strftime('%H:%M Дата - %A %d %b %Y')
    context.bot.send_message(
        chat_id=chat.id, text=(
            f'Время в Москве - {is_date_msk}'
        )
    )


def random_digit(update, context):
    """Команда вызывающая рандомное число."""
    chat = update.effective_chat
    context.bot.send_message(chat.id, random_number())


def show_my_ip(update, context):
    """Команда показывающая Ваш IP."""
    chat = update.effective_chat
    context.bot.send_message(chat.id, get_ip())


def say_hi(update, context):
    """Приветствие бота на все не зарезервированные слова."""
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='Привет, я KittyBot!')


def wake_up(update, context):
    """Команда инициализирующая меню и бота."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([
                                 ['/new_cat', '/time'],
                                 ['/show_my_ip', '/random_digit']
                                 ], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}. Посмотри, какого котика я тебе нашёл',
        reply_markup=button,
    )
    context.bot.send_photo(chat.id, get_new_image())


def main():
    """Основная логика бота."""
    try:
        updater = Updater(token=secret_token)

        updater.dispatcher.add_handler(CommandHandler('start', wake_up))
        updater.dispatcher.add_handler(
            CommandHandler('random_digit', random_digit)
        )
        updater.dispatcher.add_handler(CommandHandler('new_cat', new_cat))
        updater.dispatcher.add_handler(CommandHandler('time', date_now))
        updater.dispatcher.add_handler(CommandHandler(
            'show_my_ip', show_my_ip)
        )
        updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))

        updater.start_polling()
        updater.idle()
    except Exception as error:
        error_message = f'Произошел сбой в программе, Ошибка - {error}!'
        logger.error(error_message)
        exit()


if __name__ == '__main__':
    main()
