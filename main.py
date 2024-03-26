import functools
import telebot
import peewee
from telebot.types import Message
from API import BASE_URL, BOOK_URL
import requests
from datetime import datetime
import json
from BotFunctions.sorting_def import sorting
from Keyboards import quantity_kb, main_menu_kb, back_kb, inline_markup
from BotFunctions.welcome_def import welcome
from BotFunctions.high_func import high_books
from BotFunctions.low_func import low_books
from BotFunctions.custom_func import custom_books
from BotFunctions.title_def import title
from secrets import BOT_TOKEN
from DataBase import db, UserData, BooksCount, BooksName, UserNewData, User

bot = telebot.TeleBot(BOT_TOKEN)

with db:
    db.create_tables([UserData, BooksCount, BooksName, UserNewData, User])


@bot.message_handler(func=lambda message: message.text == 'Начать поиск \U0001F680')
def main_menu(message):
    """
    Метод вывода главного меню бота, вызывается командами: /search, /menu; а также принятыми сообщениями от
    пользователя: "Начать поиск", "Главное меню"
    В случае успешного ввода предложенных ботом команд происходит переход к методу ввода данных для поиска,
    иначе выдается сообщение об ошибке
    :param message: принятое сообщение от пользователя(команды или текстовое сообщение)
    :return: None
    """
    bot.reply_to(message, text='<b>Выбери одну из предложенных ниже команд:</b>\n\n\U00002757 '
                             'Чтобы узнать о каждой из них поподробнее, а также о работе бота, нажми на '
                             'кнопку "Помощь" \U00002757',
                     reply_markup=main_menu_kb,
                     parse_mode='html')
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.message_handler(func=lambda message: message.text == 'Поиск книги по ее названию \U0001F50E')
@bot.message_handler(commands=['search'])
def searching_title(message):
    """
    Метод для поиска книг согласно запросам пользователя, а также при получении команды "Помощь" выдает инструкцию по
    правилам пользования ботом
    :param message: принятое сообщение от пользователя
    :return: None
    """
    book_title = bot.reply_to(message, text='<b>Введите название книги на <u>АНГЛИЙСКОМ</u> языке!</b>\n\n\U00002757 '
                                    'Чем более полным будет ваше введенное название, тем более точный результат Вы '
                                    'получите! \U00002757',
                                       parse_mode='html')
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.register_next_step_handler(book_title, title)


@bot.message_handler(func=lambda message: message.text == 'История поиска \U0001F4D6')
def searching_story(message):
    with open('Ваша история поиска.txt', 'r', encoding='utf-8') as history_file:
        bot.send_document(message.chat.id, history_file, reply_markup=back_kb)

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.message_handler(func=lambda message: message.text == 'Что можно добавить? \U0001F4DD')
def searching_new(message):
    bot.reply_to(message, 'Данный бот находится на этапе раннего доступа с готовой реализацией поиска книг по их '
                          'названиям. Однако в дальнейшем будут реализованы следующие команды поиска книг:\n\n1) '
                          'Поиск всех книг введенных пользователем автора;\n\n2) Поиск книг по жанрам(тематике), '
                          'например: поиск всех книг про теннис;\n\n3) Поиск книг на различных языках мира.',
                 reply_markup=back_kb)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.message_handler(func=lambda message: message.text == 'Помощь \U00002049')
def searching_help(message):
    bot.reply_to(message, '<b>Что умеет OpenLibraryBot?</b>\n\nДля начала работы с ботом нажмите на кнопку '
                         '<b><u>"НАЧАТЬ"</u></b>.\n\nЕсли же вы уже пользовались данным ботом и снова вернулись для '
                         'поиска еще одних(ой) книг(и), то введите команду /start.\n\nПосле того как бот с '
                         'вами поздоровался и вы перешли в основное меню, вам будут предложены следующие '
                         'команды:\n\n1) <b>"Поиск книги по ее названию"</b> - по данной команде бот выдаст вам '
                         'книгу в соответствие с вашим введенным название.\n\n\U00002757 <b>ОБРАТИТЕ ВНИМАНИЕ</b> '
                         '\U00002757\nНазвания необходимо вводить <b><u>АНГЛИЙСКИМИ</u></b> буквами. Далее следуйте '
                         'согласно указаниям бота.\n\n\U00002757 ВАЖНО \U00002757\nБот является <b><u>ранней '
                         'версией</u></b>, еще множество других функций будут добавлены позже!',
                     reply_markup=back_kb,
                     parse_mode='html')
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.message_handler(func=lambda message: message.text == '<b>Введите название книги на <u>АНГЛИЙСКОМ</u> языке!</b>'
                                              '\n\n\U00002757 Чем более полным будет ваше введенное '
                                              'название, тем более точный результат Вы получите! \U00002757',
                                          parse_mode='html')
def title(message):
    """
    Метод, выводящий результат поиска ботом книг. Если количество совпадений по названию слишком большое, то бот
    предлагает выбрать количество книг, которое он выведет пользователю
    :param message: принятое сообщение от пользователя
    :return: если большое количество книг, предлагает выбрать какое именно количество вывести, иначе отправляет
    пользователю результат поиска со ссылкой на книгу
    """
    URL = BASE_URL + 'title={title}'.format(title=message.text)

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
    except peewee.IntegrityError:
        information = UserData.get(UserData.user_id == message.from_user.id)
        information.numFound = data['numFound']
        information.name = data['docs'][0]['title']
        information.link = data['docs'][0]['key']
        information.docs = data['docs']
        information.save()

    if UserData.get(UserData.user_id == message.from_user.id).numFound >= 10:
        bot.reply_to(message, '\U0001F9FE <b>Всего найдено {} книг(и)!</b> \U0001F9FE\n\nЭто слишком много, попробуйте '
                          'ввести команду /search и снова ввести более <b><u>ПОЛНОЕ НАЗВАНИЕ</u></b> книги '
                          '\U0001F4A1\n\nЛибо вы можете получить необходимое вам количество <b><u>СТАРЫХ</u></b> или '
                          '<b><u>НОВЫХ</u></b> книг, удовлетворяющих результатам вашего поиска \U00002B07'.format(
                                                UserData.get(UserData.user_id == message.from_user.id).numFound),
                     reply_markup=inline_markup,
                     parse_mode='html')
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
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


@bot.message_handler(func=lambda message: message.text == '5')
@bot.message_handler(func=lambda message: message.text == '10')
@bot.message_handler(func=lambda message: message.text == '15')
def sorting(message):
    """
    Метод для перехода к конкретной сортировке полученного результата поиска по годам первой публикации
    :param message: принятое сообщение от пользователя
    :return: При получении команды /high переходит к методу сортировки книг от самых новых к самым старым;
    /low-переходит к методу сортировки книг от самых старых к самым новым; /custom-переходит к пользовательскому методу
    сортировки книг
    """
    count = int(message.text)

    try:
        BooksCount.create(
            user_id=message.from_user.id,
            count=count,
        )
    except peewee.IntegrityError:
        information = BooksCount.get(BooksCount.user_id == message.from_user.id)
        information.count = count
        information.save()

    bot.send_message(message.chat.id, '<b>ОТЛИЧНО!</b>\n\n\U0001F50E Если вы хотите получить <b><u>{num1} САМЫХ '
                            'НОВЫХ КНИГ</u></b>, то введите команду /high\n\nЕсли же вы хотите увидеть <b><u>{num2} '
                            'САМЫХ СТАРЫХ КНИГ</u></b>, то введите команду /low\n\nТакже вы можете выбрать книги '
                            'согласно <b>ГОДУ ИХ ПЕРВОЙ ПУБЛИКАЦИИ</b>, для этого введите команду /custom '
                            '\U0001F50D'.format(
                                    num1=BooksCount.get(
                                        BooksCount.user_id == message.from_user.id).count,
                                    num2=BooksCount.get(
                                        BooksCount.user_id == message.from_user.id).count),
                                     parse_mode='html')

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.message_handler(func=lambda message: message.text == 'Главное меню \U0001F4A1')
def go_main_menu(message):
    """
    Метод для перехода в главное меню
    :param message: принятое сообщение от пользователя
    :return: переход в главное меню
    """
    bot.reply_to(message, '<b>Вы вернулись в главное меню!</b>\n\nДля продолжения работы выберите одну из '
                          'предложенных ниже команд \U00002B07',
                     reply_markup=main_menu_kb,
                     parse_mode='html')

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


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
                          (high_books, {"commands": ['high']}),
                          (low_books, {"commands": ['low']}),
                          (custom_books, {"commands": ['custom']})]


def register_func(bot, func, *args, **kwargs):
    """
    Функция регистрации методов функционирования telegram-бота
    :param bot: параметр telegram-бота
    :param func: метод функционирования бота
    :param args:  параметры, передающиеся по позиции
    :param kwargs: параметры, передающиеся по имени
    :return:
    """
    @bot.message_handler(*args, **kwargs)
    @functools.wraps(func)
    def wrapper(message: Message):
        return func(bot, message)

    return wrapper


for func, kwargs in functions_for_register:
    print(func, kwargs)
    new_func = register_func(bot, func, **kwargs)


@bot.message_handler(func=lambda message: True)
def echo_all(message: Message) -> None:
    """
    Обработчик сообщений echo_all
    :param message: принятое сообщение от пользователя
    :return: ответ бота
    """
    bot.reply_to(message, message.text)


if __name__ == '__main__':
    bot.infinity_polling()
