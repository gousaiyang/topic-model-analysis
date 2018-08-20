import os
import pathlib
import re

from decouple import config

DATA_SOURCE_DIR = config('DATA_SOURCE_DIR')
REPORT_DIR = config('REPORT_DIR')
MODEL_DIR = config('MODEL_DIR')
LOG_DIR = config('LOG_DIR')


def data_source_file(filename):
    return str(pathlib.Path(DATA_SOURCE_DIR) / filename)


def report_file(filename):
    return str(pathlib.Path(REPORT_DIR) / filename)


def model_file(filename):
    return str(pathlib.Path(MODEL_DIR) / filename)


def log_file(filename):
    return str(pathlib.Path(LOG_DIR) / filename)


def name_replace_ext(filename, newext):
    return os.path.splitext(filename)[0] + newext


def name_with_title_suffix(filename, suffix):
    title, ext = os.path.splitext(filename)
    return title + suffix + ext


def is_bad_filename(filename):
    if not filename:
        return True

    filename = filename.lower()

    if re.search(r'[<>:"/\\|?*\x00-\x1f]', filename):
        return True

    if re.fullmatch(r'con|prn|aux|nul|com[1-9]|lpt[1-9]', filename):
        return True

    if filename[-1] in ('.', ' '):
        return True

    return False
