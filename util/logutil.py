import re

from .fileutil import file_read_contents


def parse_data_from_log(logfilename, *, encoding='utf-8', regex_x=None,
                        regex_y, cast_x=str, cast_y=str):
    content = file_read_contents(logfilename, encoding=encoding)
    result_y = list(map(cast_y, re.findall(regex_y, content)))
    len_y = len(result_y)

    if regex_x is None:
        result_x = list(range(1, len_y + 1))
    else:
        result_x = list(map(cast_x, re.findall(regex_x, content)))

        if len(result_x) != len_y:
            raise ValueError('lengths of x and y are inconsistent')

    return result_x, result_y
