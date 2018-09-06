import os

from decouple import config
from flask import Flask, g, request, session

from service.auth import check_credentials, get_id_by_username
from service.models import db
from util import failure_response, success_response, validate_not_empty

os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = config('FLASK_SECRET')


@app.before_request
def before_request():
    g.db = db
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def hello():
    return 'Twitter Topic Model System'


@app.route('/api/auth', methods=['GET'])
def check_login():
    return success_response(bool(session.get('user')))


@app.route('/api/auth', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    r = validate_not_empty(username, 'username')
    if not r:
        return failure_response(str(r))

    r = validate_not_empty(password, 'password')
    if not r:
        return failure_response(str(r))

    if check_credentials(username, password):
        session['user'] = get_id_by_username(username)
        return success_response()
    else:
        return failure_response('Wrong credentials.', 401)


@app.route('/api/auth', methods=['DELETE'])
def logout():
    session.pop('user', None)
    return success_response(status_code=204)
