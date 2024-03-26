from datetime import datetime
import telebot
import peewee
from API import BOOK_URL
from Keyboards import back_kb
from DataBase import UserData, UserNewData, BooksName, BooksCount
from secrets import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)


def high_books(bot, message):
    """
    Метод сортировки в зависимости от полученной команды и выдачи результата пользователю в виде текстового документа
    :param message: принятое сообщение от пользователя
    :return: бот отправляет пользователю текстовый документ с готовым результатом поиска книг; при получении команды
    /custom подается команда для ввода промежутка лет, в котором были опубликованы конкретные книги
    """
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
    except peewee.IntegrityError:
        information = UserNewData.get(UserNewData.user_id == message.from_user.id)
        information.new_data = new_data
        information.save()

    UserNewData.get(UserNewData.user_id == message.from_user.id).new_data = sorted(
        eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data), key=lambda year: year['first_publish_year'], reverse=False)
    books = 'НОВЫХ'

    try:
        BooksName.create(
            user_id=message.from_user.id,
            name=books,
        )
    except peewee.IntegrityError:
        information = BooksName.get(BooksName.user_id == message.from_user.id)
        information.name = books
        information.save()

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    bot.send_message(message.chat.id, 'По результатам ваших запросов выше представлены <b>{count} САМЫХ {status} '
                          'КНИЖЕК</b> из открытой библиотеки \U00002705\n\n\U00002757 <b>ВНИМАНИЕ</b> \U00002757\n\n'
                          'Как только вы вернетесь в главное меню, переписка с ботом будет <b><u>АВТОМАТИЧЕСКИ '
                          'УДАЛЕНА!</u></b>'.format(
                                    count=BooksCount.get(BooksCount.user_id == message.from_user.id).count,
                                    status=BooksName.get(BooksName.user_id == message.from_user.id).name),
                              reply_markup=back_kb,
                              parse_mode='html')

    history_file = open('Ваша история поиска.txt', 'w', encoding='utf-8')

    for i_elem in range(BooksCount.get(BooksCount.user_id == message.from_user.id).count):
        bot.send_message(message.chat.id, '<b>{num}) Название</b>: {title}\n<b>Ссылка на книжку</b>: {link}\n\n'.format(
            num=i_elem + 1,
            title=eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['title'],
            link=BOOK_URL + eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['key']),
                         parse_mode='html')

        history_file.write('{date}\nНазвание: {title}\nСсылка на книжку: {link}\n\n'.format(
            date=datetime.now(),
            title=eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['title'],
            link=BOOK_URL + eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data)[i_elem]['key']))

    history_file.close()
