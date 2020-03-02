import telebot
import logging
import threading
import schedule
import time
import requests
from telebot import types
import os
from WorkWithFile import WorkWithFile

the_first_prize = WorkWithFile('nine')
the_second_prize = WorkWithFile('none')
idForAdmin = []
last_document_name = []
bot = telebot.TeleBot('925758227:AAE3Og96C06CzvjGl8KrThu1NI875LhEPks')


@bot.message_handler(commands=['start', 'help'])
def start(message):
    send = bot.send_message(message.chat.id,"\n"
                            'Здравствуйте, в данном боте вы можете найти нужную вам информацию по прайс листу.')
    keyboard(message.chat.id)


def keyboard(id):
    button_search_in__the_first_prize = types.KeyboardButton('Общий прайс')
    button_search_in__the_second_prize = types.KeyboardButton('Моторка прайс')
    keyboard_search = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard_search.add(button_search_in__the_first_prize, button_search_in__the_second_prize)
    bot.send_message(chat_id=id,
                     text='Выберите прайс для поиска, или напишите название товара или артикул',
                     reply_markup=keyboard_search)

@bot.message_handler(content_types=['text'])
def text(message):
    if 'Общий прайс' == message.text:
        send = bot.send_message(message.chat.id, 'Напишите название товара или артикуль товара')
        bot.register_next_step_handler(send, the_first_prize_result)
    elif 'Моторка прайс' == message.text:
        send = bot.send_message(message.chat.id, 'Напишите название товара или артикуль товара')
        bot.register_next_step_handler(send, the_second_prize_result)
    else:
        print(message.text)
        information(message.text, message.chat.id)


@bot.message_handler(content_types=['document'])
def update(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = message.document.file_name
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton("Общий прайс", callback_data='the_first')
        item2 = types.InlineKeyboardButton("Моторка прайс", callback_data='the_second')
        markup.add(item1, item2)
        bot.send_message(message.chat.id, 'Выберите прайс для обновления', reply_markup=markup)
        last_document_name.append(src)
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

    except Exception as e:
        bot.reply_to(message, e)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'the_first':
                if not last_document_name.__contains__(the_first_prize.name_of_file):
                    if the_first_prize.name_of_file not in the_second_prize.name_of_file and (
                            os.path.exists(the_first_prize.name_of_file)):
                        try:
                            path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                the_first_prize.name_of_file)
                            os.remove(path)
                        except PermissionError as e:
                            print("something")
                    the_first_prize.name_of_file = last_document_name[0]
            elif call.data == 'the_second':
                if not last_document_name.__contains__(the_second_prize.name_of_file):
                    if the_first_prize.name_of_file not in the_second_prize.name_of_file and (
                            os.path.exists(the_second_prize.name_of_file)):
                        try:
                            path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                the_second_prize.name_of_file)
                            os.remove(path)
                        except PermissionError as e:
                            print("something")

                    the_second_prize.name_of_file = last_document_name[0]
            # remove inline buttons
            last_document_name.clear()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Файл обновлен!",
                                  reply_markup=None)
    except Exception as e:
        bot.reply_to(call.message, e)


@bot.message_handler(commands=['search'])
def search(message):
    send = bot.send_message(message.chat.id, 'Напишите название товара или артикуль товара')
    bot.register_next_step_handler(send, information)


def the_first_prize_result(message):
    order = the_first_prize.search(message.text)
    bot.send_message(message.chat.id, order)


def the_second_prize_result(message):
    order = the_second_prize.search(message.text)
    bot.send_message(message.chat.id, order)


def information(message, id):
    first_result = the_first_prize.search(message)
    second_result = the_second_prize.search(message)
    bot.send_message(id, "Общий прайс" + "\n" + first_result + "Моторка прайс" + "\n" + second_result)


# Tread for update file every 3 hours
def main(name):
    """
    Execute run at the beggining and every hour.
    """
    try:
        run()
        schedule.every(3).hours.do(run)

        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        logging.info(e)


def run():
    try:
        file_motorka = requests.get('http://wma-united.ru/download/prajs-motorka.xlsx')
        with open('prajs-motorka.xlsx', 'wb') as new_file:
            new_file.write(file_motorka.content)
        the_first_prize.name_of_file = 'prajs-motorka.xlsx'
        logging.info('motorka ready')
        file_obcshij = requests.get('http://wma-united.ru/download/prajs-obcshij.xlsx')
        with open('prajs-obcshij.xlsx', 'wb') as new_file:
            new_file.write(file_obcshij.content)
        the_second_prize.name_of_file = 'prajs-obcshij.xlsx'
        logging.info('Update all files with threads')

    except Exception as e:
        logging.info(e)


x = threading.Thread(target=main, args=(1,))
x.start()

bot.polling(none_stop=True)
