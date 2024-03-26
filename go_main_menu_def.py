from BotFunctions.main_menu_def import main_menu
import telebot
from secrets import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(func=lambda message: message.text == 'Главное меню')
def go_main_menu(message):
    """
    Метод для перехода в главное меню
    :param message: принятое сообщение от пользователя
    :return: переход в главное меню
    """
    bot.register_next_step_handler(message.text, main_menu)
