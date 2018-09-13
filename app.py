import functools
import multiprocessing
import os
from datetime import timedelta

import colorlabels as cl
from decouple import config
from flask import Flask, g, request, send_file, session

from service.auth import check_credentials, get_id_by_username
from service.file import (get_file_by_id, get_file_info, remove_file,
                          upload_source_file)
from service.models import User, db
from service.task import (create_training_task, get_running_task,
                          get_task_by_id, get_task_info, kill_running_task)
from util import (data_source_file, failure_response, is_bad_filename,
                  success_response, validate_not_empty,
                  validate_positive_integer, validate_safe_name)

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

    r = validate_not_empty(username, 'username') and \
        validate_not_empty(password, 'password')
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
    if f.owner.id != user.id:
        return failure_response('Access denied.', 403)

    return success_response(get_file_info(f))


@app.route('/api/files/<int:file_id>/download', methods=['GET'])
@login_required
def download_file(file_id):
    user = get_current_user()

    f = get_file_by_id(file_id)
    if not f:
        return failure_response('File does not exist.', 404)
    if f.owner.id != user.id:
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
    if f.owner.id != user.id:
        return failure_response('Access denied.', 403)

    remove_file(f)
    return success_response(status_code=204)


@app.route('/api/tasks', methods=['GET'])
@login_required
def list_all_tasks():
    user = get_current_user()
    return success_response([get_task_info(t) for t in user.tasks])


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    user = get_current_user()

    task = get_task_by_id(task_id)
    if not task:
        return failure_response('Task does not exist.', 404)
    if task.owner.id != user.id:
        return failure_response('Access denied.', 403)

    return success_response(get_task_info(task))


@app.route('/api/tasks/running', methods=['GET'])
@login_required
def check_running_task():
    user = get_current_user()

    task = get_running_task()
    if task:
        if task.owner.id == user.id:
            response = {'running': True, 'task': get_task_info(task)}
        else:
            response = {'running': True}
    else:
        response = {'running': False}

    return success_response(response)


@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    user = get_current_user()

    tweets_file = request.form.get('tweets_file')
    userinfo_file = request.form.get('userinfo_file')
    tag = request.form.get('tag')
    min_topics = request.form.get('min_topics')
    max_topics = request.form.get('max_topics')
    iterations = request.form.get('iterations')
    keyword = request.form.get('keyword')

    r = validate_not_empty(tweets_file, 'tweets_file') and \
        validate_positive_integer(tweets_file, 'tweets_file') and \
        validate_not_empty(userinfo_file, 'userinfo_file') and \
        validate_positive_integer(userinfo_file, 'userinfo_file') and \
        validate_not_empty(tag, 'tag') and \
        validate_safe_name(tag, 'tag') and \
        validate_not_empty(min_topics, 'min_topics') and \
        validate_positive_integer(min_topics, 'min_topics') and \
        validate_not_empty(max_topics, 'max_topics') and \
        validate_positive_integer(max_topics, 'max_topics') and \
        validate_not_empty(iterations, 'iterations') and \
        validate_positive_integer(iterations, 'iterations') and \
        validate_not_empty(keyword, 'keyword')
    if not r:
        return failure_response(str(r))

    tweets_file = int(tweets_file)
    userinfo_file = int(userinfo_file)
    min_topics = int(min_topics)
    max_topics = int(max_topics)
    iterations = int(iterations)

    tweets_file = get_file_by_id(tweets_file)
    if not tweets_file:
        return failure_response('tweets_file does not exist.', 404)
    if tweets_file.owner.id != user.id:
        return failure_response('tweets_file access denied.', 403)
    if tweets_file.file_type != 'source':
        return failure_response('tweets_file is not a source file')

    userinfo_file = get_file_by_id(userinfo_file)
    if not userinfo_file:
        return failure_response('userinfo_file does not exist.', 404)
    if userinfo_file.owner.id != user.id:
        return failure_response('userinfo_file access denied.', 403)
    if userinfo_file.file_type != 'source':
        return failure_response('userinfo_file is not a source file')

    if min_topics < 3 or max_topics < 3:
        return failure_response('the number of topics should be at least 3')

    if min_topics > max_topics:
        return failure_response('require min_topics <= max_topics')

    params = {
        'min_topics': min_topics,
        'max_topics': max_topics,
        'iterations': iterations,
        'keyword': keyword
    }

    with multiprocessing.Lock():
        if get_running_task():
            return failure_response('A task is already running on the server.')

        r = create_training_task(user, tweets_file, userinfo_file, tag, params)
        if r:
            return success_response(r, 201)
        else:
            return failure_response('A task with the same tag already exists.')


@app.route('/api/tasks/running', methods=['DELETE'])
@login_required
def terminate_running_task():
    user = get_current_user()

    task = get_running_task()
    if not task:
        return failure_response('No running tasks.', 404)
    if task.owner.id != user.id:
        return failure_response('Access denied.', 403)

    kill_running_task()
    return success_response(status_code=204)


@app.route('/api/<path:path>')
def api_error_handler(path):
    return failure_response('Invalid API endpoint.', 404)
