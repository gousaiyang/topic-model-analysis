import traceback


def get_exc_line():
    return traceback.format_exc().splitlines()[-1]
