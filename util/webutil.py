import os
import webbrowser
from urllib.request import pathname2url


def open_html_in_browser(filename):
    webbrowser.open('file:' + pathname2url(os.path.abspath(filename)))
