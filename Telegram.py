import telebot
import functools

import requests
import json

from datetime import datetime

from BotFunctions.welcome_def import welcome
from BotFunctions.main_menu_def import main_menu
from BotFunctions.searching_def import searching
from BotFunctions.title_def import title
from BotFunctions.sorting_def import sorting
from BotFunctions.your_books_def import your_books
from BotFunctions.custom_search_def import custom_search
from BotFunctions.go_main_menu_def import go_main_menu

from DataBase import UserData, BooksCount, BooksName, UserNewData, User, db, database
from secrets import BOT_TOKEN
from API import BASE_URL, BOOK_URL

from Keyboards import start_kb, main_menu_kb, back_kb, inline_markup, quantity_kb


# Подключаем бота
bot = telebot.TeleBot(BOT_TOKEN)

with db:
    db.create_tables([UserData, BooksCount, BooksName, UserNewData, User])


# @bot.message_handler(commands=['start'])
# def welcome(message: Message) -> None:
#     """
#     Метод приветствия OpenLibraryBot, вызывается вводом команды /start
#     :param message: полученное от пользователя сообщение
#     :return: keyboard (клавиатура главного меню), происходит переход в главное меню бота
#     """
#     try:
#         User.create(
#             user_id=message.from_user.id,
#             first_name=message.from_user.first_name,
#             last_name=message.from_user.last_name,
#             username=message.from_user.username,
#         )
#         # Приветствуем нового пользователя
#         bot.reply_to(message,
#                          f'{message.from_user.first_name}, добро пожаловать в OpenLibraryBot!\n\nЗдесь вы можете найти '
#                          'любую интересующую вас книгу, попробовать узнать для себя новых авторов и их самые '
#                          'популярные произведения.\n\nЧтобы начать работу, нажмите на кнопку ниже ⬇️',
#                          reply_markup=start_kb)
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#     except IntegrityError:
#         # Приветствуем старого пользователя
#         bot.reply_to(message, f'С возвращением, {message.from_user.first_name}!'
#                                      '\n\nЧтобы начать работу, нажмите на кнопку ниже ⬇️', reply_markup=start_kb)
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#     return start_kb
#
#
# @bot.message_handler(content_types=['text'])
# @bot.message_handler(commands=['search', 'menu'])
# def main_menu(message):
#     """
#     Метод вывода главного меню бота, вызывается командами: /search, /menu; а также принятыми сообщениями от
#     пользователя: "Начать поиск", "Главное меню"
#
#     :param message: принятое сообщение от пользователя
#     :return: в случае успешного ввода предложенных ботом команд происходит переход к методу ввода данных для поиска, иначе
#     выдается сообщение об ошибке
#     """
#     # if message.text == 'Удалить результаты поиска':
#     #     for i_del in range(BooksCount.get(BooksCount.user_id == message.from_user.id).count + 2):
#     #         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - i_del)
#
#     if message.text == 'Начать поиск' or message.text == '/search' or message.text == '/menu':
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#
#     elif message.text == 'Главное меню':
#         for i_del in range(BooksCount.get(BooksCount.user_id == message.from_user.id).count + 2):
#             bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - i_del)
#
#     else:
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#         bot.send_message(message.chat.id, 'Ой, что-то пошло не так, попробуйте ввести команду /search')
#
#     mesg = bot.send_message(message.chat.id, 'Выбери одну из предложенных ниже команд:\n\nЧтобы узнать '
#                                            'о каждой из них поподробнее, а также о работе бота, нажми на '
#                                            'кнопку "Помощь".', reply_markup=main_menu_kb)
#     bot.register_next_step_handler(mesg, searching)
#
#
# @bot.message_handler(content_types=['text'])
# def searching(message):
#     """
#     Метод для поиска книг согласно запросам пользователя, а также при получении команды "Помощь" выдает инструкцию по
#     правилам пользования ботом
#     :param message: принятое сообщение от пользователя
#     :return:
#     """
#     bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
#     bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#
#     if message.text == 'Поиск книги по ее названию':
#         name_msg = bot.send_message(message.chat.id, 'Введите название книги на АНГЛИЙСКОМ языке.\n\nP.S. Чем более '
#                                                 'полным будет ваше введенное название, тем более точный результат Вы '
#                                                 'получите!')
#         bot.register_next_step_handler(name_msg, title)
#
#     elif message.text == 'История поиска' or message.text == '/history':
#         with open('Ваша история поиска.txt', 'r', encoding='utf-8') as history_file:
#             bot.send_document(message.chat.id, history_file, reply_markup=back_kb)
#
#     elif message.text == 'Что можно добавить?':
#         bot.send_message(message.chat.id, 'Данный бот находится на этапе раннего доступа с готовой '
#                                                       'реализацией поиска книг по их названиям. Однако в дальнейшем '
#                                                       'будут реализованы следующие команды поиска книг:\n\n1) Поиск '
#                                                       'всех книг введенных пользователем автора;\n\n2) Поиск книг '
#                                                       'по жанрам(тематике), например: поиск всех книг про теннис;\n\n'
#                                                       '3) Поиск книг на различных языках мира.', reply_markup=back_kb)
#
#     elif message.text == 'Помощь' or message.text == '/help':
#         bot.send_message(message.chat.id,
#                          'Что умеет OpenLibraryBot?\n\nДля начала работы с ботом нажмите на кнопку '
#                          '"НАЧАТЬ".\n\nЕсли же вы уже пользовались данным ботом и снова вернулись для '
#                          'поиска еще одних(ой) книг(и), то введите команду /start.\n\nПосле того как бот с '
#                          'вами поздоровался и вы перешли в основное меню, вам будут предложены следующие '
#                          'команды:\n\n1) "Поиск книги по ее названию" - по данной команде бот выдаст вам '
#                          'книгу в соответствие с вашим введенным название. ОБРАТИТЕ ВНИМАНИЕ, что '
#                          'названия необходимо вводить АНГЛИЙСКИМИ буквами. Далее следуйте согласно '
#                          'указаниям бота.', reply_markup=back_kb)
#     else:
#         bot.send_message(message.chat.id, 'Я не знаю ответ на данный вопрос...')
#
#
# @bot.message_handler(content_types=['text'])
# def title(message):
#     """
#     Метод, выводящий результат поиска ботом книг. Если количество совпадений по названию слишком большое, то бот
#     предлагает выбрать количество книг, которое он выведет пользователю
#     :param message: принятое сообщение от пользователя
#     :return: если большое количество книг, предлагает выбрать какое именно количество вывести, иначе отправляет
#     пользователю результат поиска со ссылкой на книгу
#     """
#     URL = BASE_URL + 'title={title}'.format(title=message.text)
#
#     response = requests.get(URL)
#     data_resp = json.loads(response.text)
#
#     with open('titles.json', 'w') as file:
#         json.dump(data_resp, file, indent=4)
#
#     with open('titles.json', 'r') as file:
#         data = json.load(file)
#
#     try:
#         UserData.create(
#             user_id=message.from_user.id,
#             numFound=data['numFound'],
#             name=data['docs'][0]['title'],
#             link=data['docs'][0]['key'],
#             docs=data['docs'],
#         )
#     except IntegrityError:
#         information = UserData.get(UserData.user_id == message.from_user.id)
#         information.numFound = data['numFound']
#         information.name = data['docs'][0]['title']
#         information.link = data['docs'][0]['key']
#         information.docs = data['docs']
#         information.save()
#
#     if UserData.get(UserData.user_id == message.from_user.id).numFound >= 10:
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#         bot.send_message(message.chat.id, 'Всего найдено {} книг(и)!\n\nЭто слишком много, попробуйте ввести'
#                                           ' более полное название с помощью команды /search\n\nЛибо вы можете получить '
#                                           'необходимое вам количество старых или новых книг, удовлетворяющих '
#                                           'результатам вашего поиска ⬇️'.format(
#                                            UserData.get(UserData.user_id == message.from_user.id).numFound), reply_markup=inline_markup)
#
#     else:
#         history_file = open('Ваша история поиска.txt', 'a', encoding='utf-8')
#         history_file.write('{date}\nНазвание: {name}\nСсылка: {link}\n\n'.format(
#             date=datetime.now(),
#             name=UserData.get(UserData.user_id == message.from_user.id).name,
#             link=BOOK_URL + UserData.get(UserData.user_id == message.from_user.id).link
#         ))
#         history_file.close()
#         bot.send_message(message.chat.id, 'Книга успешно найдена!\n\nПереходите по ссылке: {}'.format(
#             BOOK_URL + UserData.get(UserData.user_id == message.from_user.id).link), reply_markup=back_kb)
#
#
# @bot.callback_query_handler(func=lambda call: True)
# def how_many(call):
#     """
#     Метод, который запрашивает у пользователя сколько именно книг вывести в случае большого результата поиска
#     :param call: данные функции обратного вызова
#     :return: переходит к методу сортировки полученного результата
#     """
#     if call.message:
#         if call.data == 'count':
#             bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
#             msg = bot.send_message(call.message.chat.id, 'Сколько книг вы хотите получить?', reply_markup=quantity_kb)
#             bot.register_next_step_handler(msg, sorting)
#
#
# @bot.message_handler(content_types=['text'])
# def sorting(message):
#     """
#     Метод для перехода к конкретной сортировке полученного результата поиска по годам первой публикации
#     :param message: принятое сообщение от пользователя
#     :return: При получении команды /high переходит к методу сортировки книг от самых новых к самым старым;
#     /low-переходит к методу сортировки книг от самых старых к самым новым; /custom-переходит к пользовательскому методу
#     сортировки книг
#     """
#     count = int(message.text)
#
#     try:
#         BooksCount.create(
#             user_id=message.from_user.id,
#             count=count,
#         )
#     except IntegrityError:
#         information = BooksCount.get(BooksCount.user_id == message.from_user.id)
#         information.count = count
#         information.save()
#
#     bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
#     bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#     msg = bot.send_message(message.chat.id, 'Отлично!\n\nЕсли вы хотите получить {num1} самых новых книг, то введите '
#                                             'команду /high\n\nЕсли же вы хотите увидеть {num2} самых старых книг, '
#                                             'то введите команду /low\n\nТакже вы можете выбрать книги согласно году '
#                                             'их первой публикации, для этого введите команду /custom'.format(
#                                                                 num1=BooksCount.get(
#                                                                     BooksCount.user_id == message.from_user.id).count,
#                                                                 num2=BooksCount.get(
#                                                                     BooksCount.user_id == message.from_user.id).count))
#
#     bot.register_next_step_handler(msg, your_books)
#
#
# @bot.message_handler(commands=['high', 'low', 'custom'])
# def your_books(message):
#     """
#     Метод сортировки в зависимости от полученной команды и выдачи результата пользователю в виде текстового документа
#     :param message: принятое сообщение от пользователя
#     :return: бот отправляет пользователю текстовый документ с готовым результатом поиска книг; при получении команды
#     /custom подается команда для ввода промежутка лет, в котором были опубликованы конкретные книги
#     """
#     bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
#     bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#
#     new_data = []
#
#     for i_elem in eval(UserData.get(UserData.user_id == message.from_user.id).docs):
#         try:
#             if isinstance(i_elem['first_publish_year'], int):
#                 new_data.append(i_elem)
#         except KeyError:
#             print('Повреждение ключа!')
#
#     try:
#         UserNewData.create(
#             user_id=message.from_user.id,
#             new_data=new_data,
#         )
#     except IntegrityError:
#         information = UserNewData.get(UserNewData.user_id == message.from_user.id)
#         information.new_data = new_data
#         information.save()
#
#     if message.text == '/high':
#         UserNewData.get(UserNewData.user_id == message.from_user.id).new_data = sorted(
#             eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data), key=lambda year: year['first_publish_year'])
#         books = 'новых'
#
#         try:
#             BooksName.create(
#                 user_id=message.from_user.id,
#                 name=books,
#             )
#         except IntegrityError:
#             information = BooksName.get(BooksName.user_id == message.from_user.id)
#             information.name = books
#             information.save()
#
#     elif message.text == '/low':
#         UserNewData.get(UserNewData.user_id == message.from_user.id).new_data = sorted(
#             eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data), key=lambda year: year['first_publish_year'], reverse=True)
#         books = 'старых'
#
#         try:
#             BooksName.create(
#                 user_id=message.from_user.id,
#                 name=books,
#             )
#         except IntegrityError:
#             information = BooksName.get(BooksName.user_id == message.from_user.id)
#             information.name = books
#             information.save()
#
#     elif message.text == '/custom':
#         years_msg = bot.send_message(message.chat.id, 'Введите диапозон лет, например: "1976 1988"')
#         bot.register_next_step_handler(years_msg, custom_search)
#
#     if message.text == '/high' or message.text == '/low':
#         history_file = open('Ваша история поиска.txt', 'w', encoding='utf-8')
#
#         for i_elem in range(BooksCount.get(BooksCount.user_id == message.from_user.id).count):
#             bot.send_message(message.chat.id, '{num}) Название: {title}\nСсылка на книжку: {link}\n\n'.format(
#                 num=i_elem + 1,
#                 title=eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['title'],
#                 link=BOOK_URL + eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['key']))
#
#             history_file.write('{date}\nНазвание: {title}\nСсылка на книжку: {link}\n\n'.format(
#                 date=datetime.now(),
#                 title=eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['title'],
#                 link=BOOK_URL + eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['key']))
#
#         bot.send_message(message.chat.id, 'По результатам ваших запросов выше представлены {count} самых {status} '
#                                           'книжек из открытой библиотеки: ⬆\n\nP.S. Как только вы вернетесь в главное '
#                                           'меню, переписка с ботом будет автоматически удалена!'.format(
#                                             count=BooksCount.get(BooksCount.user_id == message.from_user.id).count,
#                                             status=BooksName.get(BooksName.user_id == message.from_user.id).name), reply_markup=back_kb)
#
#         history_file.close()
#
#
# @bot.message_handler(content_types=['text'])
# def custom_search(message):
#     """
#     Метод пользовательского поиска книг по принятому промежутку первых публикаций книг
#     :param message: принятое сообщение от пользователя
#     :return: бот отправляет пользователю текстовый документ с готовым результатом поиска книг
#     """
#     bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
#     bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#     years = message.text.split()
#     max_count = 0
#
#     history_file = open('Ваша история поиска.txt', 'w', encoding='utf-8')
#     for i_key in eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data):
#         if int(years[0]) <= int(i_key['first_publish_year']) <= int(years[1]):
#             if max_count == BooksCount.get(BooksCount.user_id == message.from_user.id).count:
#                 break
#             else:
#                 max_count += 1
#                 bot.send_message(message.chat.id, '{num}) Название: {title};\nГод публикации: {publish_year};\nСсылка '
#                                                   'на книжку: {link}\n\n'.format(
#                                                         num=max_count,
#                                                         title=i_key['title'],
#                                                         publish_year=i_key['first_publish_year'],
#                                                         link=BOOK_URL + i_key['key']
#                                                     ), reply_markup=back_kb)
#
#                 history_file.write('{date}\nНазвание: {title}\nСсылка на книжку: {link}\n\n'.format(
#                                     date=datetime.now(),
#                                     title=i_key['title'],
#                                     link=BOOK_URL + i_key['key']
#                                 ))
#
#     if max_count == 0:
#         err_msg = bot.send_message(message.chat.id, 'К сожалению нет книжек, удовлетворяющих результатам вашего '
#                                                     'поиска...\n\nПопробуйте еще раз ввести другие года первых '
#                                                     'публикаций, например: "1976 1988"')
#         bot.register_next_step_handler(err_msg, custom_search)
#     else:
#         bot.send_message(message.chat.id, 'По результатам ваших запросов выше представлены {count} книжек в диапозоне '
#                                           'от {left_board} до {right_board} годов публикаций из '
#                                           'открытой библиотеки: ⬆'.format(
#                                             count=max_count,
#                                             left_board=int(years[0]),
#                                             right_board=int(years[1])))
#
#     history_file.close()
#
#
# @bot.message_handler(content_types=['text'])
# def go_main_menu(message):
#     """
#     Метод для перехода в главное меню
#     :param message: принятое сообщение от пользователя
#     :return: переход в главное меню
#     """
#     if message.text == 'Главное меню':
#         bot.register_next_step_handler(message.text, main_menu)


@bot.callback_query_handler(func=lambda call: True)
def how_many(call):
    """
    Метод, который запрашивает у пользователя сколько именно книг вывести в случае большого результата поиска
    :param call: данные функции обратного вызова
    :return: переходит к методу сортировки полученного результата
    """
    if call.message:
        if call.data == 'count':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            msg = bot.send_message(call.message.chat.id, 'Сколько книг вы хотите получить?', reply_markup=quantity_kb)
            bot.register_next_step_handler(msg, sorting)


functions_for_register = [(welcome, {"commands": ['start']}),
                          (main_menu, {"commands": ['search']}),
                          (main_menu, {"commands": ['menu']}),
                          (main_menu, {"content_types": ['text']}),
                          (searching, {"content_types": ['text']}),
                          (title, {"content_types": ['text']}),
                          (sorting, {"content_types": ['text']}),
                          (your_books, {"commands": ['high']}),
                          (your_books, {"commands": ['low']}),
                          (your_books, {"commands": ['custom']}),
                          (custom_search, {"content_types": ['text']}),
                          (go_main_menu, {"content_types": ['text']})]


def register_funcs(bot, func, *args, **kwargs):
    @bot.message_handler(*args, **kwargs)
    @functools.wraps(func)
    def wrapper(message):
        return func(bot, message)
    return wrapper


for func, kwargs in functions_for_register:
    new_func = register_funcs(bot, func, **kwargs)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """
    Обработчик сообщений echo_all
    :param message: принятое сообщение от пользователя
    :return: ответ бота
    """
    bot.reply_to(message, message.text)


if __name__ == '__main__':
    bot.infinity_polling()
