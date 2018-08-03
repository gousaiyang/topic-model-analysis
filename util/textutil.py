import re

URL_PATTERN = r'[a-zA-Z][-0-9a-zA-Z+.]*://' \
              r'([-0-9a-zA-Z]+\.)*[-0-9a-zA-Z]+' \
              r'(/[\x21-\x7e]*)?'

EMAIL_PATTERN = r'[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+' \
                r'@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*'


def merge_whitespaces(text):
    return re.sub(r'\s+', ' ', text)


def remove_non_asciiprintable(text, sub=''):
    return re.sub(r'[^\x20-\x7e]+', sub, text)


def remove_urls(text, sub=''):
    return re.sub(URL_PATTERN, sub, text)


def remove_twitter_pic_urls(text, sub=''):
    return re.sub(r'pic\.twitter\.com/[0-9a-zA-Z]+', sub, text)


def remove_emails(text, sub=''):
    return re.sub(EMAIL_PATTERN, sub, text)


def remove_html_comments(text, sub=''):
    return re.sub(r'<!--.*?-->', sub, text)


def remove_markdown_codeblocks(text, sub=''):
    return re.sub(r'```.*?```', sub, text)


def rank(x):
    assert isinstance(x, int)
    assert x > 0

    if x % 10 == 1 and x % 100 != 11:
        return '%dst' % x
    elif x % 10 == 2 and x % 100 != 12:
        return '%dnd' % x
    elif x % 10 == 3 and x % 100 != 13:
        return '%drd' % x
    else:
        return '%dth' % x
