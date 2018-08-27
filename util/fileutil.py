import json


def file_read_contents(filename, encoding='utf-8'):
    with open(filename, 'r', encoding=encoding) as fin:
        return fin.read()


def file_read_lines(filename, encoding='utf-8', strip_newline=True):
    with open(filename, 'r', encoding=encoding) as fin:
        for line in fin:
            if strip_newline:
                yield line.rstrip('\n')
            else:
                yield line


def file_read_json(filename, encoding='utf-8'):
    with open(filename, 'r', encoding=encoding) as fin:
        return json.load(fin)


def file_write_contents(filename, content, encoding='utf-8'):
    with open(filename, 'w', encoding=encoding) as fout:
        fout.write(content)


def file_write_lines(filename, content, encoding='utf-8', append_newline=True):
    with open(filename, 'w', encoding=encoding) as fout:
        for line in content:
            fout.write(line)

            if append_newline:
                fout.write('\n')


def file_write_json(filename, content, encoding='utf-8'):
    with open(filename, 'w', encoding=encoding) as fout:
        json.dump(content, fout)
