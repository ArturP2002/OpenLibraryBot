from BotFunctions.main_menu_def import main_menu
import telebot
from secrets import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)


# @bot.message_handler(content_types=['text'])
def go_main_menu(bot, message):
    """
    Метод для перехода в главное меню
    :param message: принятое сообщение от пользователя
    :return: переход в главное меню
    """
    if message.text == 'Главное меню':
        bot.register_next_step_handler(message.text, main_menu)
