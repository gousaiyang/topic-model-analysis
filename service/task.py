import json
import multiprocessing
import os
import sys
import traceback

import colorlabels as cl

from main import (plot_diff_topics, text_preprocessor_twlda, twitter_lda,
                  visualization_twlda)
from util import get_exc_line, is_windows, log_file, pipe_encoding, report_file

from .models import (STATUS_FAILED, STATUS_FINISHED, STATUS_RUNNING, File,
                     Task, User, db)


def training_task_process(task_id, user_id, tweets_filename, userinfo_filename,
                          tag, params):
    task = get_task_by_id(task_id)
    logfilename = 'tasklog-%d.log' % task_id

    try:
        logfile = open(log_file(logfilename), 'w', encoding='utf-8')
    except Exception:
        traceback.print_exc()
        update_task_status(task, code=STATUS_FAILED,
                           detail='Error: %s' % get_exc_line())
        return

    try:
        sys.stdout = logfile
        sys.stderr = logfile

        cl.config(color_span=0)
        cl.info('Task started, pid is %d' % os.getpid())

        update_task_status(task, code=STATUS_RUNNING, detail='Preprocessing')
        text_preprocessor_twlda(tweets_filename[:-4], tweet_min_length=2,
                                user_min_tweets=1, remove_duplicates=True)

        desc_prefix = '%d-%s' % (user_id, tag)
        num_topics_range = list(range(params['min_topics'],
                                      params['max_topics'] + 1))

        for topics in num_topics_range:
            update_task_status(task, detail='Training: %d topics' % topics)
            twitter_lda(output_desc='%s-%d' % (desc_prefix, topics),
                        topics=topics, iteration=params['iterations'],
                        show_console_output=False)

        update_task_status(task, detail='Analyzing: plotting perplexity')
        plot_filename = plot_diff_topics(num_topics_range, desc_prefix,
                                         r'Perplexity is ([\d.]+)',
                                         pipe_encoding)

        user = User.get_by_id(user_id)

        with db.atomic():
            f = File.create(file_type='plot', owner=user,
                            original_name='ldaplot-%s.png' % tag,
                            physical_name=plot_filename,
                            size=os.stat(report_file(plot_filename)).st_size)
            task.plot = f
            task.save()

        report_ids = []

        for topics in num_topics_range:
            update_task_status(task, detail='Analyzing: generating report for '
                                            '%d topics' % topics)
            report = visualization_twlda(params['keyword'],
                                         '%s-%d' % (desc_prefix, topics),
                                         '%s-%d' % (tag, topics),
                                         userinfo_filename, open_browser=False)

            with db.atomic():
                f = File.create(file_type='report', owner=user,
                                original_name=report, physical_name=report,
                                size=os.stat(report_file(report)).st_size)

            report_ids.append(f.id)

        with db.atomic():
            task.reports = json.dumps(report_ids)
            task.save()

        update_task_status(task, code=STATUS_FINISHED, detail='Finished')
    except Exception:
        traceback.print_exc()
        update_task_status(task, code=STATUS_FAILED,
                           detail='Error: %s' % get_exc_line())
    finally:
        logfile.close()


def get_task_by_id(task_id):
    return Task.get_or_none(Task.id == task_id)


def get_task_info(task):
    return {
        'id': task.id,
        'tweets_file': task.tweets_file.id,
        'userinfo_file': task.userinfo_file.id,
        'tag': task.tag,
        'params': json.loads(task.params),
        'status_code': task.status_code,
        'status_detail': task.status_detail,
        'plot': task.plot.id if task.plot else None,
        'reports': json.loads(task.reports),
        'created_at': task.created_at
    }


def get_running_task():
    tasks = multiprocessing.active_children()
    return get_task_by_id(tasks[0].task_id) if tasks else None


def create_training_task(user, tweets_file, userinfo_file, tag, params):
    with db.atomic():
        if Task.select().where((Task.owner == user) & (Task.tag == tag)):
            return False

        t = Task.create(owner=user, tweets_file=tweets_file,
                        userinfo_file=userinfo_file, tag=tag,
                        params=json.dumps(params), status_detail='Created')

    p = multiprocessing.Process(target=training_task_process,
                                args=(t.id, user.id, tweets_file.physical_name,
                                      userinfo_file.physical_name, tag,
                                      params))
    p.task_id = t.id
    p.start()

    return t.id


def update_task_status(task, *, code=None, detail=None):
    with db.atomic():
        if code is not None:
            task.status_code = code
        if detail is not None:
            task.status_detail = detail
        task.save()
