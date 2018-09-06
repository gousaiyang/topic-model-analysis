import os
import webbrowser
from urllib.request import pathname2url

from flask import jsonify, make_response


def open_html_in_browser(filename):
    webbrowser.open('file:' + pathname2url(os.path.abspath(filename)))


def success_response(message=None, status_code=200):
    if message is None:
        return '', status_code
    else:
        return make_response(jsonify(message), status_code)


def failure_response(message=None, status_code=400):
    if message is None:
        return '', status_code
    else:
        return make_response(jsonify(message), status_code)
