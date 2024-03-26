from sqlite3 import IntegrityError
import telebot
from API import BASE_URL, BOOK_URL
import requests
from datetime import datetime
import json
from DataBase import UserData
from Keyboards import back_kb, inline_markup
from secrets import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)


# @bot.message_handler(content_types=['text'])
def title(bot, message):
    """
    Метод, выводящий результат поиска ботом книг. Если количество совпадений по названию слишком большое, то бот
    предлагает выбрать количество книг, которое он выведет пользователю
    :param message: принятое сообщение от пользователя
    :return: если большое количество книг, предлагает выбрать какое именно количество вывести, иначе отправляет
    пользователю результат поиска со ссылкой на книгу
    """
    if not message.text.startswith('/'):

        URL = BASE_URL + 'title={title}'.format(title=message.from_user.id.text)

        response = requests.get(URL)
        data_resp = json.loads(response.text)

        with open('titles.json', 'w') as file:
            json.dump(data_resp, file, indent=4)

        with open('titles.json', 'r') as file:
            data = json.load(file)

        try:
            UserData.create(
                user_id=message.from_user.id,
                numFound=data['numFound'],
                name=data['docs'][0]['title'],
                link=data['docs'][0]['key'],
                docs=data['docs'],
            )
        except IntegrityError:
            information = UserData.get(UserData.user_id == message.from_user.id)
            information.numFound = data['numFound']
            information.name = data['docs'][0]['title']
            information.link = data['docs'][0]['key']
            information.docs = data['docs']
            information.save()

        if UserData.get(UserData.user_id == message.from_user.id).numFound >= 10:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.reply_to(message, 'Всего найдено {} книг(и)!\n\nЭто слишком много, попробуйте ввести'
                                  ' более полное название с помощью команды /search\n\nЛибо вы можете получить '
                                  'необходимое вам количество старых или новых книг, удовлетворяющих '
                                  'результатам вашего поиска ⬇️'.format(
            UserData.get(UserData.user_id == message.from_user.id).numFound), reply_markup=inline_markup)
        else:
            history_file = open('Ваша история поиска.txt', 'a', encoding='utf-8')
            history_file.write('{date}\nНазвание: {name}\nСсылка: {link}\n\n'.format(
                date=datetime.now(),
                name=UserData.get(UserData.user_id == message.from_user.id).name,
                link=BOOK_URL + UserData.get(UserData.user_id == message.from_user.id).link
            ))
            history_file.close()
            bot.reply_to(message, 'Книга успешно найдена!\n\nПереходите по ссылке: {}'.format(
                BOOK_URL + UserData.get(UserData.user_id == message.from_user.id).link), reply_markup=back_kb)
