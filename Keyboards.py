import telebot

# Клавиатура главного меню
main_menu_kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button_title = telebot.types.KeyboardButton(text='Поиск книги по ее названию \U0001F50E')
button_history = telebot.types.KeyboardButton(text='История поиска \U0001F4D6')
button_something = telebot.types.KeyboardButton(text='Что можно добавить? \U0001F4DD')
button_support = telebot.types.KeyboardButton(text='Помощь \U00002049')
main_menu_kb.add(button_title)
main_menu_kb.add(button_history)
main_menu_kb.add(button_something)
main_menu_kb.add(button_support)

# Кнопка возврата в главное меню
back_kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button_back = telebot.types.KeyboardButton(text='Главное меню \U0001F4A1')
back_kb.add(button_back)

# Инлайн клавиатура для перехода к выбору количества книг
inline_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
res_count = telebot.types.InlineKeyboardButton('Выбрать количество книг', callback_data='count')
inline_markup.add(res_count)

# Клавиатура выбора количества книг
quantity_kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
five = telebot.types.KeyboardButton('5')
ten = telebot.types.KeyboardButton('10')
fifteen = telebot.types.KeyboardButton('15')
quantity_kb.add(five, ten, fifteen)

# Кнопка начала работы
start_kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button_start = telebot.types.KeyboardButton(text='Начать поиск \U0001F680')
start_kb.add(button_start)
