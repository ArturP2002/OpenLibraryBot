import telebot
from telebot.types import Message
from Keyboards import back_kb
from BotFunctions.title_def import title
from secrets import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)


# @bot.message_handler(content_types=['text'])
def searching(bot, message):
    """
    Метод для поиска книг согласно запросам пользователя, а также при получении команды "Помощь" выдает инструкцию по
    правилам пользования ботом
    :param message: принятое сообщение от пользователя
    :return: None
    """
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    if message.text == 'Поиск книги по ее названию \U0001F50E':
        book_title = bot.send_message(message.chat.id, text='<b>Введите название книги на АНГЛИЙСКОМ языке!</b>'
                                                                 '\n\n\U00002757 Чем более полным будет ваше введенное '
                                                                 'название, тем более точный результат Вы'
                                                                 ' получите! \U00002757',
                                                            parse_mode='html')
        bot.register_next_step_handler(book_title, title)
        # bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
        # bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    elif message.text == 'История поиска \U0001F4D6':
        with open('Ваша история поиска.txt', 'r', encoding='utf-8') as history_file:
            bot.send_document(message.chat.id, history_file, reply_markup=back_kb)

    elif message.text == 'Что можно добавить? \U0001F4DD':
        bot.send_message(message.from_user.id, 'Данный бот находится на этапе раннего доступа с готовой реализацией поиска книг по их '
                              'названиям. Однако в дальнейшем будут реализованы следующие команды поиска книг:\n\n1) '
                              'Поиск всех книг введенных пользователем автора;\n\n2) Поиск книг по жанрам(тематике), '
                              'например: поиск всех книг про теннис;\n\n3) Поиск книг на различных языках мира.',
                     reply_markup=back_kb)

    elif message.text == 'Помощь \U00002049':
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.send_message(message.from_user.id, 'Что умеет OpenLibraryBot?\n\nДля начала работы с ботом нажмите на кнопку '
                             '"НАЧАТЬ".\n\nЕсли же вы уже пользовались данным ботом и снова вернулись для '
                             'поиска еще одних(ой) книг(и), то введите команду /start.\n\nПосле того как бот с '
                             'вами поздоровался и вы перешли в основное меню, вам будут предложены следующие '
                             'команды:\n\n1) "Поиск книги по ее названию" - по данной команде бот выдаст вам '
                             'книгу в соответствие с вашим введенным название. <b>ОБРАТИТЕ ВНИМАНИЕ</b>'
                             'названия необходимо вводить АНГЛИЙСКИМИ буквами. Далее следуйте согласно '
                             'указаниям бота.',
                         reply_markup=back_kb,
                         parse_mode='html')

    # else:
    #     bot.send_message(message.chat.id, 'Я не знаю ответ на данный вопрос...\n\nВведите команду /search')
