from sqlite3 import IntegrityError
import telebot
from DataBase import BooksCount
from BotFunctions.your_books_def import your_books
from secrets import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)


# @bot.message_handler(content_types=['text'])
def sorting(bot, message):
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
    except IntegrityError:
        information = BooksCount.get(BooksCount.user_id == message.from_user.id)
        information.count = count
        information.save()

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    msg = bot.send_message(message.chat.id, 'Отлично!\n\nЕсли вы хотите получить {num1} самых новых книг, то введите '
                                            'команду /high\n\nЕсли же вы хотите увидеть {num2} самых старых книг, '
                                            'то введите команду /low\n\nТакже вы можете выбрать книги согласно году '
                                            'их первой публикации, для этого введите команду /custom'.format(
                                                                num1=BooksCount.get(
                                                                    BooksCount.user_id == message.from_user.id).count,
                                                                num2=BooksCount.get(
                                                                    BooksCount.user_id == message.from_user.id).count))

    bot.register_next_step_handler(msg, your_books)