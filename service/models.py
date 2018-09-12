import datetime

from decouple import config
from peewee import (BigIntegerField, CharField, DateTimeField, ForeignKeyField,
                    IntegerField, Model, SmallIntegerField, SqliteDatabase)

db = SqliteDatabase(config('DB_FILENAME'))


class BaseModel(Model):
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class User(BaseModel):
    username = CharField()
    password = CharField()


class File(BaseModel):
    file_type = CharField(column_name='type')
    owner = ForeignKeyField(User, backref='files')
    original_name = CharField()
    physical_name = CharField()
    size = BigIntegerField()


STATUS_FAILED = -1
STATUS_CREATED = 0
STATUS_RUNNING = 1
STATUS_FINISHED = 2


class Task(BaseModel):
    owner = ForeignKeyField(User, backref='tasks')
    tweets_file = ForeignKeyField(File)
    userinfo_file = ForeignKeyField(File)
    tag = CharField()
    params = CharField()
    status_code = SmallIntegerField(default=STATUS_CREATED)
    status_detail = CharField()
    plot = ForeignKeyField(File, null=True)
    reports = CharField(default='[]')


all_models = BaseModel.__subclasses__()


def create_tables():
    with db:
        db.create_tables(all_models)


def drop_tables():
    with db:
        db.drop_tables(all_models)
