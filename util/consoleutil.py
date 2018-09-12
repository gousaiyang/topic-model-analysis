import os
import platform
import shlex
import sys

stdout_backup = None
stderr_backup = None
devnull = None
is_windows = platform.system() == 'Windows'
pipe_encoding = 'utf-16-le' if is_windows else 'utf-8'


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


def escape_param(s):
    if is_windows:
        return "'%s'" % s.replace("'", "''")  # For PowerShell
    else:
        return shlex.quote(s)


def exec_shell(s):
    if is_windows:
        return ['powershell', s]
    else:
        return ['/bin/sh', '-c', s]


def tee_command(command, filename):
    return exec_shell(command + ' 2>&1 | tee ' + escape_param(filename))


def redirect_command(command, filename):
    return exec_shell(command + ' 2>&1 > ' + escape_param(filename))
