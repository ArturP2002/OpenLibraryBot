from datetime import datetime
from sqlite3 import IntegrityError
import telebot
from API import BOOK_URL
from Keyboards import back_kb
from DataBase import UserData, UserNewData, BooksName, BooksCount
from BotFunctions.custom_search_def import custom_search
from secrets import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)


# @bot.message_handler(commands=['high', 'low', 'custom'])
def your_books(bot, message):
    """
    Метод сортировки в зависимости от полученной команды и выдачи результата пользователю в виде текстового документа
    :param message: принятое сообщение от пользователя
    :return: бот отправляет пользователю текстовый документ с готовым результатом поиска книг; при получении команды
    /custom подается команда для ввода промежутка лет, в котором были опубликованы конкретные книги
    """
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    new_data = []

    for i_elem in eval(UserData.get(UserData.user_id == message.from_user.id).docs):
        try:
            if isinstance(i_elem['first_publish_year'], int):
                new_data.append(i_elem)
        except KeyError:
            print('Повреждение ключа!')

    try:
        UserNewData.create(
            user_id=message.from_user.id,
            new_data=new_data,
        )
    except IntegrityError:
        information = UserNewData.get(UserNewData.user_id == message.from_user.id)
        information.new_data = new_data
        information.save()

    if message.text == '/high':
        UserNewData.get(UserNewData.user_id == message.from_user.id).new_data = sorted(
            eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data), key=lambda year: year['first_publish_year'])
        books = 'новых'

        try:
            BooksName.create(
                user_id=message.from_user.id,
                name=books,
            )
        except IntegrityError:
            information = BooksName.get(BooksName.user_id == message.from_user.id)
            information.name = books
            information.save()

    elif message.text == '/low':
        UserNewData.get(UserNewData.user_id == message.from_user.id).new_data = sorted(
            eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data), key=lambda year: year['first_publish_year'], reverse=True)
        books = 'старых'

        try:
            BooksName.create(
                user_id=message.from_user.id,
                name=books,
            )
        except IntegrityError:
            information = BooksName.get(BooksName.user_id == message.from_user.id)
            information.name = books
            information.save()

    elif message.text == '/custom':
        years_msg = bot.send_message(message.chat.id, 'Введите диапозон лет, например: "1976 1988"')
        bot.register_next_step_handler(years_msg, custom_search)

    if message.text == '/high' or message.text == '/low':
        history_file = open('Ваша история поиска.txt', 'w', encoding='utf-8')

        for i_elem in range(BooksCount.get(BooksCount.user_id == message.from_user.id).count):
            bot.send_message(message.chat.id, '{num}) Название: {title}\nСсылка на книжку: {link}\n\n'.format(
                num=i_elem + 1,
                title=eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['title'],
                link=BOOK_URL + eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['key']))

            history_file.write('{date}\nНазвание: {title}\nСсылка на книжку: {link}\n\n'.format(
                date=datetime.now(),
                title=eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['title'],
                link=BOOK_URL + eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['key']))

        bot.send_message(message.chat.id, 'По результатам ваших запросов выше представлены {count} самых {status} '
                                          'книжек из открытой библиотеки: ⬆\n\nP.S. Как только вы вернетесь в главное '
                                          'меню, переписка с ботом будет автоматически удалена!'.format(
                                            count=BooksCount.get(BooksCount.user_id == message.from_user.id).count,
                                            status=BooksName.get(BooksName.user_id == message.from_user.id).name), reply_markup=back_kb)

        history_file.close()
