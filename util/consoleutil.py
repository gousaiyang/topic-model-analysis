import os
import sys

stdout_backup = None
stderr_backup = None
devnull = None


def disable_console_output():
    global stdout_backup
    global stderr_backup
    global devnull

    if stdout_backup or stderr_backup or devnull:
        return

    stdout_backup = sys.stdout
    stderr_backup = sys.stderr
    devnull = open(os.devnull, 'w')
    sys.stdout = devnull
    sys.stderr = devnull


def enable_console_output():
    global stdout_backup
    global stderr_backup
    global devnull

    if not (stdout_backup and stderr_backup and devnull):
        return

    sys.stdout = stdout_backup
    sys.stderr = stderr_backup
    devnull.close()
    stdout_backup = None
    stderr_backup = None
    devnull = None


class NoConsoleOutput:
    def __enter__(self):
        disable_console_output()

    def __exit__(self, type_, value, trace):
        enable_console_output()
