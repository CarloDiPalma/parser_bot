import datetime
import os
import telebot
import pandas as pd
import sqlite3
from telebot import types

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    """Подключение кнопки."""
    markup = types.ReplyKeyboardMarkup()
    button = types.KeyboardButton("Загрузить файл")
    markup.add(button)

    bot.send_message(
        message.chat.id,
        "Привет, {0.first_name}!".format(
            message.from_user
        ),
        reply_markup=markup
    )


@bot.message_handler(content_types=['text'])
def save_file(message):
    if message.text == 'Загрузить файл':
        bot.send_message(message.chat.id, 'Вставьте файл')


@bot.message_handler(content_types=['document'])
def save_file(message):
    """Сохранение файла."""

    try:
        chat_id = message.chat.id
        file_info = bot.get_file(message.document.file_id)
        file_name, file_extenstion = os.path.splitext(file_info.file_path)
        now = datetime.datetime.now()

        downloaded_file = bot.download_file(file_info.file_path)
        src = 'files/' + now.strftime('%d-%m-%Y') + file_extenstion
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "Файл сохранён")
        read_exel_by_pd(src, message)
    except Exception as e:
        bot.reply_to(message, e)


def read_exel_by_pd(path, message):
    """Чтение файла и создание датафрейма."""

    df = pd.read_excel(path)
    insert_data_to_db(df)
    send_msg(message, df)


def send_msg(message, df):
    for index, row in df.iterrows():
        line = row.get('title') + '\n' + row.get('url') + '\n' + row.get(
            'xpath')
        bot.send_message(message.chat.id, line)


def insert_data_to_db(df):
    """Сохранение данных в БД."""

    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    for index, row in df.iterrows():
        title = row.get('title')
        url = row.get('url')
        xpath = row.get('xpath')
        cur.execute(
            f'INSERT INTO sites ('
            f'title, url, xpath'
            f') values ("{title}", "{url}", "{xpath}")'
        )
        conn.commit()
    conn.close()



# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


def main() -> None:
    """Активация бота."""
    bot.infinity_polling()


if __name__ == '__main__':
    main()
