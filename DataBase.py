from peewee import *

# База данных всех пользователей
db = SqliteDatabase('users.db')

# Делаем базу данных для хранения данных
database = SqliteDatabase('user_data.db') # Создаем базу данных


class BaseModelData(Model):
    """
    Базовый класс для поисковых моделей пользователей
    """
    user_id = IntegerField(primary_key=True)

    class Meta:
        database = database
        order_by = 'user_id'


class UserData(BaseModelData):
    numFound = IntegerField()
    name = CharField()
    link = CharField()
    docs = CharField()

    class Meta:
        db_table = 'data'


class BooksCount(BaseModelData):
    count = IntegerField()

    class Meta:
        db_table = 'count'


class BooksName(BaseModelData):
    name = CharField()

    class Meta:
        db_table = 'books_name'


class UserNewData(BaseModelData):
    new_data = CharField()

    class Meta:
        db_table = 'new_data'


class BaseModelUser(Model):
    """
    Базовый класс для базы данных модели пользователя
    """
    class Meta:
        database = db


class User(BaseModelUser):
    """
    Модель пользователя
    :arg user_id: ID пользователя,
         first_name: имя пользователя в Telegram
         last_name: фамилия пользователя(если есть) в Telegram
         username: никнейм пользователя в Telegram

    """
    user_id = IntegerField(primary_key=True)
    first_name = CharField()
    last_name = CharField(null=True)
    username = CharField()
