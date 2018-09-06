import bcrypt

from .models import User, db


def register(username, password):
    with db.atomic():
        if User.select().where(User.username == username):
            return False

        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        User.create(username=username, password=password)
        return True


def check_credentials(username, password):
    result = User.select().where(User.username == username)
    return result and bcrypt.checkpw(password.encode(),
                                     result[0].password.encode())


def get_id_by_username(username):
    result = User.select().where(User.username == username)
    return result[0].id if result else None
