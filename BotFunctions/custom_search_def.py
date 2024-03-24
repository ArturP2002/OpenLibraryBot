from datetime import datetime
import telebot
from API import BOOK_URL
from DataBase import UserNewData, BooksCount
from Keyboards import back_kb
from secrets import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)


# @bot.message_handler(content_types=['text'])
def custom_search(bot, message):
    """
    Метод пользовательского поиска книг по принятому промежутку первых публикаций книг
    :param message: принятое сообщение от пользователя
    :return: бот отправляет пользователю текстовый документ с готовым результатом поиска книг
    """
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    years = message.text.split()
    max_count = 0

    history_file = open('Ваша история поиска.txt', 'w', encoding='utf-8')
    for i_key in eval(UserNewData.get(UserNewData.user_id == message.from_user.id).new_data):
        if int(years[0]) <= int(i_key['first_publish_year']) <= int(years[1]):
            if max_count == BooksCount.get(BooksCount.user_id == message.from_user.id).count:
                break
            else:
                max_count += 1
                bot.send_message(message.chat.id, '{num}) Название: {title};\nГод публикации: {publish_year};\nСсылка '
                                                  'на книжку: {link}\n\n'.format(
                                                        num=max_count,
                                                        title=i_key['title'],
                                                        publish_year=i_key['first_publish_year'],
                                                        link=BOOK_URL + i_key['key']
                                                    ), reply_markup=back_kb)

                history_file.write('{date}\nНазвание: {title}\nСсылка на книжку: {link}\n\n'.format(
                                    date=datetime.now(),
                                    title=i_key['title'],
                                    link=BOOK_URL + i_key['key']
                                ))

    if max_count == 0:
        err_msg = bot.send_message(message.chat.id, 'К сожалению нет книжек, удовлетворяющих результатам вашего '
                                                    'поиска...\n\nПопробуйте еще раз ввести другие года первых '
                                                    'публикаций, например: "1976 1988"')
        bot.register_next_step_handler(err_msg, custom_search)
    else:
        bot.send_message(message.chat.id, 'По результатам ваших запросов выше представлены {count} книжек в диапозоне '
                                          'от {left_board} до {right_board} годов публикаций из '
                                          'открытой библиотеки: ⬆'.format(
                                            count=max_count,
                                            left_board=int(years[0]),
                                            right_board=int(years[1])))

    history_file.close()
