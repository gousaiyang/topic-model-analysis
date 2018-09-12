import re
import string


class ValidationResult:
    def __init__(self, message=None):
        if message is None:
            self.valid = True
            self.message = ''
        else:
            self.valid = False
            self.message = str(message)

    def __bool__(self):
        return self.valid

    def __str__(self):
        return self.message

    def __repr__(self):
        return '<ValidationResult valid=%r, message=%r>' % (self.valid,
                                                            self.message)


def validate_not_empty(value, field):
    if value:
        return ValidationResult()
    else:
        return ValidationResult('%s should not be empty' % field)


def validate_positive_integer(value, field):
    if re.fullmatch(r'[0-9]+', value):
        return ValidationResult()
    else:
        return ValidationResult('%s should be a positive integer' % field)


def validate_safe_name(value, field):
    if re.fullmatch(r'[-_0-9a-zA-Z]+', value):
        return ValidationResult()
    else:
        return ValidationResult('%s should only contain letters, digits, '
                                'underscores and hyphens.' % field)


def validate_username(username):
    if re.fullmatch(r'[-_0-9a-zA-Z]{5,20}', username):
        return ValidationResult()
    else:
        return ValidationResult('Username should be 5 to 20 characters that '
                                'only contain letters, digits, underscores '
                                'and hyphens.')


def validate_password(password):
    if len(password) < 8:
        return ValidationResult('Password should be at least 8 characters.')

    for charset in (string.digits, string.ascii_lowercase,
                    string.ascii_uppercase, string.punctuation):
        if not any(c in password for c in charset):
            return ValidationResult('Password should contain digits, '
                                    'lowercase and uppercase letters, '
                                    'and special characters.')

    return ValidationResult()
