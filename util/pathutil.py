import os
import pathlib
import re

from decouple import config

DATA_SOURCE_DIR = pathlib.Path(config('DATA_SOURCE_DIR'))
REPORT_DIR = pathlib.Path(config('REPORT_DIR'))
MODEL_DIR = pathlib.Path(config('MODEL_DIR'))
LOG_DIR = pathlib.Path(config('LOG_DIR'))
TWLDA_BASE_DIR = pathlib.Path(config('TWLDA_BASE_DIR'))
TWLDA_DATA_DIR = pathlib.Path(config('TWLDA_DATA_DIR'))
TWLDA_SOURCE_DIR = pathlib.Path(config('TWLDA_SOURCE_DIR'))
TWLDA_RESULT_DIR = pathlib.Path(config('TWLDA_RESULT_DIR'))


def data_source_file(filename):
    return str(DATA_SOURCE_DIR / filename)


def report_file(filename):
    return str(REPORT_DIR / filename)


def model_file(filename):
    return str(MODEL_DIR / filename)


def log_file(filename):
    return str(LOG_DIR / filename)


def twlda_base_file(filename):
    return str(TWLDA_BASE_DIR / filename)


def twlda_data_file(filename):
    return str(TWLDA_BASE_DIR / TWLDA_DATA_DIR / filename)


def twlda_source_file(filename):
    return str(TWLDA_BASE_DIR / TWLDA_SOURCE_DIR / filename)


def twlda_result_file(filename):
    return str(TWLDA_BASE_DIR / TWLDA_RESULT_DIR / filename)


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
