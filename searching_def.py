import telebot
from sqlite3 import IntegrityError
from datetime import datetime
import requests
from API import BASE_URL, BOOK_URL
import json
from DataBase import UserData
# from telebot.types import Message
from Keyboards import back_kb, inline_markup
from BotFunctions.title_def import title
from secrets import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(func=lambda message: message.text == 'Поиск книги по ее названию \U0001F50E')
def searching_title(message):
    """
    Метод для поиска книг согласно запросам пользователя, а также при получении команды "Помощь" выдает инструкцию по
    правилам пользования ботом
    :param message: принятое сообщение от пользователя
    :return: None
    """
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    # if message.text == 'Поиск книги по ее названию \U0001F50E':
    book_title = bot.reply_to(message, text='<b>Введите название книги на АНГЛИЙСКОМ языке!</b>\n\n\U00002757 Чем более'
                                            ' полным будет ваше введенное название, тем более точный результат Вы '
                                            'получите! \U00002757',
                                       parse_mode='html')
    bot.register_next_step_handler(book_title, title)


@bot.message_handler(func=lambda message: message.text == 'История поиска \U0001F4D6')
def searching_story(message):
    # elif message.text == 'История поиска \U0001F4D6':
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    with open('Ваша история поиска.txt', 'r', encoding='utf-8') as history_file:
        bot.send_document(message.chat.id, history_file, reply_markup=back_kb)


@bot.message_handler(func=lambda message: message.text == 'Что можно добавить? \U0001F4DD')
def searching_new(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.reply_to(message, 'Данный бот находится на этапе раннего доступа с готовой реализацией поиска книг по их '
                          'названиям. Однако в дальнейшем будут реализованы следующие команды поиска книг:\n\n1) '
                          'Поиск всех книг введенных пользователем автора;\n\n2) Поиск книг по жанрам(тематике), '
                          'например: поиск всех книг про теннис;\n\n3) Поиск книг на различных языках мира.',
                 reply_markup=back_kb)


@bot.message_handler(func=lambda message: message.text == 'Помощь \U00002049')
def searching_help(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.reply_to(message, 'Что умеет OpenLibraryBot?\n\nДля начала работы с ботом нажмите на кнопку '
                         '"НАЧАТЬ".\n\nЕсли же вы уже пользовались данным ботом и снова вернулись для '
                         'поиска еще одних(ой) книг(и), то введите команду /start.\n\nПосле того как бот с '
                         'вами поздоровался и вы перешли в основное меню, вам будут предложены следующие '
                         'команды:\n\n1) "Поиск книги по ее названию" - по данной команде бот выдаст вам '
                         'книгу в соответствие с вашим введенным название. <b>ОБРАТИТЕ ВНИМАНИЕ</b>'
                         'названия необходимо вводить АНГЛИЙСКИМИ буквами. Далее следуйте согласно '
                         'указаниям бота.',
                     reply_markup=back_kb,
                     parse_mode='html')


@bot.message_handler(content_types=['text'])
def title(message):
    """
    Метод, выводящий результат поиска ботом книг. Если количество совпадений по названию слишком большое, то бот
    предлагает выбрать количество книг, которое он выведет пользователю
    :param message: принятое сообщение от пользователя
    :return: если большое количество книг, предлагает выбрать какое именно количество вывести, иначе отправляет
    пользователю результат поиска со ссылкой на книгу
    """
    user_text = bot.reply_to(message, '<b>Вы ввели следующий текст:</b>\n{text}'.format(
        text=message.text))
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
        bot.register_next_step_handler(user_text, many_books)
    else:
        bot.register_next_step_handler(user_text, only_book)


@bot.message_handler(content_types=['text'])
def many_books(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.reply_to(message, 'Всего найдено {} книг(и)!\n\nЭто слишком много, попробуйте ввести'
                          ' более полное название с помощью команды /search\n\nЛибо вы можете получить '
                          'необходимое вам количество старых или новых книг, удовлетворяющих '
                          'результатам вашего поиска ⬇️'.format(
        UserData.get(UserData.user_id == message.from_user.id).numFound), reply_markup=inline_markup)


@bot.message_handler(content_types=['text'])
def only_book(message):
    history_file = open('Ваша история поиска.txt', 'a', encoding='utf-8')
    history_file.write('{date}\nНазвание: {name}\nСсылка: {link}\n\n'.format(
        date=datetime.now(),
        name=UserData.get(UserData.user_id == message.from_user.id).name,
        link=BOOK_URL + UserData.get(UserData.user_id == message.from_user.id).link
    ))
    history_file.close()
    bot.reply_to(message, 'Книга успешно найдена!\n\nПереходите по ссылке: {}'.format(
        BOOK_URL + UserData.get(UserData.user_id == message.from_user.id).link), reply_markup=back_kb)
