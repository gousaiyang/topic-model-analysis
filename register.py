import sys

import colorlabels as cl

from service.auth import register
from util import validate_password, validate_username

if __name__ == '__main__':
    if len(sys.argv) < 3:
        cl.warning('Usage: %s username password' % sys.argv[0])
        sys.exit(-1)

    username = sys.argv[1]
    password = sys.argv[2]

    r = validate_username(username)
    if not r:
        cl.error(str(r))
        sys.exit(-1)

    r = validate_password(password)
    if not r:
        cl.error(str(r))
        sys.exit(-1)

    if register(username, password):
        cl.success('Successfully registered user %r.' % username)
    else:
        cl.error('User %r already exists!' % username)
