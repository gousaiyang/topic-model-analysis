import ast
import json
import re
import time

import colorlabels as cl

from util import (csv_reader, data_source_file, file_read_contents,
                  file_read_lines, file_write_contents, open_html_in_browser,
                  re_sub_literal, report_file, twlda_result_file,
                  twlda_source_file, visual_file)


def parse_user_topic(desc, encoding='utf-8'):
    logfilename = twlda_result_file('%s/TopicsDistributionOnUsers.txt' % desc)
    user_topic = []

    for line in file_read_lines(logfilename, encoding=encoding):
        data_line = line.strip().split('\t')

        if not data_line:
            continue

        data_line[0] = data_line[0][:-4]  # Remove '.txt'
        data_line[1:] = list(map(float, data_line[1:]))
        user_topic.append(data_line)

    return user_topic


def parse_topic_words(desc, encoding='utf-8'):
    topic_words = {}
    logfilename = twlda_result_file('%s/WordsInTopics.txt' % desc)
    content = file_read_contents(logfilename, encoding=encoding)
    result = re.findall(r'Topic (\d+):' + r'\t(\S+)\t([\d.]+)\n' * 30, content)

    for item in result:
        topic_words[int(item[0])] = [(word, float(prob)) for word, prob in
                                     zip(*([iter(item[1:])] * 2))]

    return topic_words


def load_user_info(userinfofile):
    user_info = {}

    for row in csv_reader(userinfofile):
        row['favourites_count'] = int(row['favourites_count'])
        row['followers_count'] = int(row['followers_count'])
        row['friends_count'] = int(row['friends_count'])
        row['listed_count'] = int(row['listed_count'])
        row['statuses_count'] = int(row['statuses_count'])
        row['verified'] = ast.literal_eval(row['verified'])
        user_info[row['screen_name']] = row

    return user_info


def show_topic_words(topic_words, topic_id):
    sum_prob = sum(p for w, p in topic_words[topic_id])
    return [{
        'word': w,
        'prob': p / sum_prob,
    } for w, p in topic_words[topic_id]]


def organize_data(desc, user_topic, topic_words, user_info, topusers=10):
    num_topics = len(topic_words)

    topics = [{
        'id': i,
        'words': show_topic_words(topic_words, i),
        'users': []
    } for i in range(num_topics)]

    for i, topic in enumerate(topics):
        user_topic = sorted(user_topic, key=lambda x: x[i + 1], reverse=True)

        for item in user_topic[:topusers]:
            sourcefilename = twlda_source_file('%s/%s.txt' % (desc, item[0]))
            text = file_read_contents(sourcefilename)
            topic['users'].append({
                            'username': item[0],
                            'weight': item[i + 1],
                            'info': user_info.get(item[0]) or {},
                            'text': text
                        })

        topic['weight'] = sum(item[i + 1] for item in user_topic)

    topics = sorted(topics, key=lambda x: x['weight'], reverse=True)

    for i, topic in enumerate(topics):
        topic['rank'] = i + 1

    return topics


def export_html(keyword, desc, data, open_browser):
    data = json.dumps({
        'title': '%s - %s' % (keyword, desc),
        'topics': data,
        'currentUser': {'info': {}}
    })
    template = file_read_contents(visual_file('template.html'))
    data = re_sub_literal(r'var data =(.*)', 'var data = ' + data, template)

    reportfile = 'ldavisual-%s-%s-%s.html' % (keyword, desc,
                                              time.strftime('%Y%m%d%H%M%S'))
    reportfile = report_file(reportfile)
    file_write_contents(reportfile, data)
    cl.success('Visualization saved as: %s' % reportfile)

    if open_browser:
        open_html_in_browser(reportfile)


def visualization_twlda(keyword, desc, userinfofile, encoding='utf-8',
                        open_browser=True):
    cl.section('Twitter-LDA Visualization')

    user_topic = parse_user_topic(desc, encoding=encoding)
    topic_words = parse_topic_words(desc, encoding=encoding)
    user_info = load_user_info(data_source_file(userinfofile))
    result = organize_data('test', user_topic, topic_words, user_info)
    export_html(keyword, desc, result, open_browser)
