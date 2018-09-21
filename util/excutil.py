import traceback

import colorlabels as cl


def get_exc_line():
    return traceback.format_exc().splitlines()[-1]


def retry_until_success(func, *args, **kwargs):
    MAX_RETRY = 2
    retry = 0
    ret = None

    while True:
        try:
            try:
                ret = func(*args, **kwargs)
            except KeyboardInterrupt:
                raise
            except Exception:
                if retry >= MAX_RETRY:
                    cl.error('Error: %sMax retries exceeded, terminating.'
                             % traceback.format_exc())
                    raise

                cl.error('Error: %sRetrying...' % traceback.format_exc())
                retry += 1
            else:
                return ret
        except KeyboardInterrupt:
            cl.warning('User hit Ctrl-C, terminating function %r'
                       % func.__name__)
            raise
