import telebot
import peewee
from DataBase import UserData, UserNewData, BooksCount
from API import BOOK_URL
from Keyboards import back_kb
from datetime import datetime
from secrets import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)


def custom_books(bot, message):
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

    years_msg = bot.reply_to(message, '<b>Введите <u>ДИАПОЗОН</u> лет</b>:\n\n\U00002757 <b>НАПРИМЕР</b> \U00002757\n\n1976 1988',
                 parse_mode='html')

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.register_next_step_handler(years_msg, custom_search)


@bot.message_handler(func=lambda message: message.text == '<b>Введите <u>ДИАПОЗОН</u> лет</b>:\n\n\U00002757 '
                                                          '<b>НАПРИМЕР</b> \U00002757\n\n1976 1988')
@bot.message_handler(commands=['custom_search'])
def custom_search(message):
    """
    Метод пользовательского поиска книг по принятому промежутку первых публикаций книг
    :param message: принятое сообщение от пользователя
    :return: бот отправляет пользователю текстовый документ с готовым результатом поиска книг
    """
    years = message.text.split()
    max_count = 0

    history_file = open('Ваша история поиска.txt', 'w', encoding='utf-8')
    for i_key in eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data):
        if int(years[0]) <= int(i_key['first_publish_year']) <= int(years[1]):
            if max_count == BooksCount.get(BooksCount.user_id == message.from_user.id).count:
                break
            else:
                max_count += 1
                bot.send_message(message.chat.id, '<b>{num}) Название:</b> {title};\n<b>Год публикации:</b> '
                                      '{publish_year};\n<b>Ссылка на книжку:</b> {link}\n\n'.format(
                                                        num=max_count,
                                                        title=i_key['title'],
                                                        publish_year=i_key['first_publish_year'],
                                                        link=BOOK_URL + i_key['key']
                                                    ),
                                 reply_markup=back_kb,
                                 parse_mode='html')

                history_file.write('{date}\nНазвание: {title}\nСсылка на книжку: {link}\n\n'.format(
                                    date=datetime.now(),
                                    title=i_key['title'],
                                    link=BOOK_URL + i_key['key']))

    if max_count == 0:
        bot.send_message(message.chat.id, 'К сожалению <b>НЕТ</b> книжек, удовлетворяющих результатам вашего '
                                        'поиска...\U0001F61F\n\nПопробуйте ввести команду /custom_search и еще раз '
                                        'ввести <b><u>ДАТЫ ПУБЛИКАЦИЙ</u></b>',
                                   parse_mode='html')

        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    else:
        bot.reply_to(message, 'По результатам ваших запросов выше представлены <b>{count} книжек в диапозоне '
                          'от {left_board} до {right_board} годов публикаций</b> из '
                          'открытой библиотеки \U00002705\n\n\U00002757 <b>ВНИМАНИЕ</b> \U00002757\n\n'
                          'Как только вы вернетесь в главное меню, переписка с ботом будет <b><u>АВТОМАТИЧЕСКИ '
                          'УДАЛЕНА!</u></b>'.format(
                                            count=max_count,
                                            left_board=int(years[0]),
                                            right_board=int(years[1])),
                     parse_mode='html')

        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    history_file.close()

