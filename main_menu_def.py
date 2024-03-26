import telebot
from DataBase import BooksCount
from Keyboards import main_menu_kb
from secrets import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)


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
    # if message.text == 'Начать поиск \U0001F680':
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.reply_to(message, text='<b>Выбери одну из предложенных ниже команд:</b>\n\n\U00002757 '
                             'Чтобы узнать о каждой из них поподробнее, а также о работе бота, нажми на '
                             'кнопку "Помощь" \U00002757',
                     reply_markup=main_menu_kb,
                     parse_mode='html')

    # elif message.text == 'Главное меню':
    #     for i_del in range(BooksCount.get(BooksCount.user_id == message.from_user.id).count + 2):
    #         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - i_del)

    # else:
    #     bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    #     bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    #     bot.send_message(message.chat.id, 'Ой, что-то пошло не так, попробуйте ввести команду /search')


    # bot.register_next_step_handler(mesg, searching)
