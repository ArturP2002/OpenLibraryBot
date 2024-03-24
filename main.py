import functools
import telebot
from telebot.types import Message
from BotFunctions.sorting_def import sorting
from Keyboards import quantity_kb
from BotFunctions.welcome_def import welcome
from BotFunctions.main_menu_def import main_menu
from BotFunctions.searching_def import searching
from BotFunctions.title_def import title
from BotFunctions.your_books_def import your_books
from BotFunctions.custom_search_def import custom_search
from BotFunctions.go_main_menu_def import go_main_menu
from secrets import BOT_TOKEN
from DataBase import db, UserData, BooksCount, BooksName, UserNewData, User

bot = telebot.TeleBot(BOT_TOKEN)

with db:
    db.create_tables([UserData, BooksCount, BooksName, UserNewData, User])


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
                          (main_menu, {"content_types": ['text']}),
                          (searching, {"content_types": ['text']}),
                          (title, {"content_types": ['text']}),
                          (sorting, {"content_types": ['text']}),
                          (your_books, {"commands": ['high']}),
                          (your_books, {"commands": ['low']}),
                          (your_books, {"commands": ['custom']}),
                          (custom_search, {"content_types": ['text']}),
                          (go_main_menu, {"content_types": ['text']})]


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
