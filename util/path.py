import pathlib

from decouple import config

DATA_SOURCE_DIR = config('DATA_SOURCE_DIR')
REPORT_DIR = config('REPORT_DIR')
MODEL_DIR = config('MODEL_DIR')


def data_source_file(filename):
    return str(pathlib.Path(DATA_SOURCE_DIR) / filename)


def report_file(filename):
    return str(pathlib.Path(REPORT_DIR) / filename)


def model_file(filename):
    return str(pathlib.Path(MODEL_DIR) / filename)
