import functools
import os
from datetime import timedelta

import colorlabels as cl
from decouple import config
from flask import Flask, g, request, send_file, session

from service.auth import check_credentials, get_id_by_username
from service.file import (get_file_by_id, get_file_info, remove_file,
                          upload_source_file)
from service.models import User, db
from util import (data_source_file, failure_response, is_bad_filename,
                  success_response, validate_not_empty)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = config('FLASK_SECRET')
app.config['MAX_CONTENT_LENGTH'] = config('MAX_UPLOAD_SIZE', cast=int)
cl.config(color_span=0)
SESSION_EXPIRE_TIME = config('SESSION_EXPIRE_TIME', cast=int)


def get_current_user():
    if session.get('user'):
        return User.get(User.id == session['user'])
    else:
        return None


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('user'):
            return failure_response('Authentication required.', 401)
        return func(*args, **kwargs)
    return wrapper


@app.before_request
def before_request():
    session.permanent = True
    session.modified = True
    app.permanent_session_lifetime = timedelta(seconds=SESSION_EXPIRE_TIME)
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


@app.route('/api/files', methods=['GET'])
@login_required
def list_all_files():
    user = get_current_user()
    return success_response([get_file_info(f) for f in user.files])


@app.route('/api/files/<int:file_id>', methods=['GET'])
@login_required
def get_file(file_id):
    user = get_current_user()

    f = get_file_by_id(file_id)
    if not f:
        return failure_response('File does not exist.', 404)
    if f.owner != user:
        return failure_response('Access denied.', 403)

    return success_response(get_file_info(f))


@app.route('/api/files/<int:file_id>/download', methods=['GET'])
@login_required
def download_file(file_id):
    user = get_current_user()

    f = get_file_by_id(file_id)
    if not f:
        return failure_response('File does not exist.', 404)
    if f.owner != user:
        return failure_response('Access denied.', 403)

    physical_path = data_source_file(f.physical_name)
    if not os.path.isfile(physical_path):
        return failure_response('File is missing on server.', 500)

    return send_file(physical_path, as_attachment=True,
                     attachment_filename=f.original_name)


@app.route('/api/files', methods=['POST'])
@login_required
def upload_file():
    user = get_current_user()

    f = request.files.get('file')

    if not f or not f.filename:
        return failure_response('No file uploaded.')

    if is_bad_filename(f.filename):
        return failure_response('Invalid filename.')

    if not f.filename.lower().endswith('.csv'):
        return failure_response("File extension should be '.csv'.")

    r = upload_source_file(f, user)
    if r:
        return success_response(r, 201)
    else:
        return failure_response('Filename already exists.')


@app.route('/api/files/<int:file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    user = get_current_user()

    f = get_file_by_id(file_id)
    if not f:
        return failure_response('File does not exist.', 404)
    if f.owner != user:
        return failure_response('Access denied.', 403)

    remove_file(f)
    return success_response(status_code=204)
