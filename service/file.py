import contextlib
import os

from util import data_source_file, random_filename, report_file

from .models import File, db


def alloc_filename(user, ext, path_func):
    while True:
        new_filename = '%d-%s%s' % (user.id, random_filename(), ext)
        new_filepath = path_func(new_filename)

        if not os.path.exists(new_filepath):
            break

    return new_filename, new_filepath


def get_file_by_id(file_id):
    return File.get_or_none(File.id == file_id)


def get_file_info(f):
    return {
        'id': f.id,
        'type': f.file_type,
        'name': f.original_name,
        'size': f.size,
        'created_at': f.created_at
    }


def get_file_path(f):
    if f.file_type == 'source':
        path = data_source_file(f.physical_name)
    elif f.file_type in ('plot', 'report'):
        path = report_file(f.physical_name)
    else:
        path = ''

    return os.path.isfile(path) and path


def upload_source_file(f, user):
    with db.atomic():
        if File.select().where((File.owner == user) &
                               (File.original_name == f.filename)):
            return False

        new_filename, new_filepath = alloc_filename(user, '.csv',
                                                    data_source_file)
        f.save(new_filepath)
        f = File.create(file_type='source', owner=user,
                        original_name=f.filename, physical_name=new_filename,
                        size=os.stat(new_filepath).st_size)

        return f.id


def remove_file(f):
    with db.atomic():
        filepath = data_source_file(f.physical_name)
        f.delete_instance()

    with contextlib.suppress(FileNotFoundError):
        os.remove(filepath)
