import datetime

from decouple import config
from peewee import (BigIntegerField, CharField, DateTimeField, ForeignKeyField,
                    Model, SqliteDatabase)

db = SqliteDatabase(config('DB_FILENAME'))


class BaseModel(Model):
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class User(BaseModel):
    username = CharField()
    password = CharField()


class File(BaseModel):
    file_type = CharField()
    owner = ForeignKeyField(User, backref='files')
    original_name = CharField()
    physical_name = CharField()
    size = BigIntegerField()


class Task(BaseModel):
    owner = ForeignKeyField(User, backref='tasks')
    tweets_file = ForeignKeyField(File)
    userinfo_file = ForeignKeyField(File)
    tag = CharField()
    params = CharField()


all_models = BaseModel.__subclasses__()


def create_tables():
    with db:
        db.create_tables(all_models)


def drop_tables():
    with db:
        db.drop_tables(all_models)
