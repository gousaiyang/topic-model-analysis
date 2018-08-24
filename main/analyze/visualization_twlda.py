import json
import re

import colorlabels as cl

from util import (re_sub_literal, report_file, twlda_result_file,
                  twlda_source_file, visual_file)


def parse_user_topic(desc, encoding='utf-8'):
    logfilename = twlda_result_file('%s/TopicsDistributionOnUsers.txt' % desc)
    user_topic = []

    with open(logfilename, 'r', encoding=encoding) as logfile:
        for line in logfile:
            data_line = line.strip().split('\t')

            if not data_line:
                continue

            data_line[0] = data_line[0][:-4]  # Remove '.txt'
            data_line[1:] = list(map(float, data_line[1:]))
            user_topic.append(data_line)

    return user_topic


def parse_topic_words(desc, encoding='utf-8'):
    logfilename = twlda_result_file('%s/WordsInTopics.txt' % desc)
    topic_words = {}

    with open(logfilename, 'r', encoding=encoding) as logfile:
        content = logfile.read()

    result = re.findall(r'Topic (\d+):' + r'\t(\S+)\t([\d.]+)\n' * 30, content)
    for item in result:
        topic_words[int(item[0])] = [(word, float(prob)) for word, prob in
                                     zip(*([iter(item[1:])] * 2))]

    return topic_words


def organize_data(desc, user_topic, topic_words, topusers=10):
    num_topics = len(topic_words)

    topics = [{
        'id': i,
        'words': [item[0] for item in topic_words[i]],
        'users': []
    } for i in range(num_topics)]

    for i, topic in enumerate(topics):
        user_topic = sorted(user_topic, key=lambda x: x[i + 1], reverse=True)

        for item in user_topic[:topusers]:
            sourcefilename = twlda_source_file('%s/%s.txt' % (desc, item[0]))

            with open(sourcefilename, 'r', encoding='utf-8') as sourcefile:
                text = sourcefile.read()

            topic['users'].append({'username': item[0], 'text': text})

        topic['weight'] = sum(item[i + 1] for item in user_topic)

    topics = sorted(topics, key=lambda x: x['weight'], reverse=True)

    for i, topic in enumerate(topics):
        topic['rank'] = i + 1

    return topics


def export_html(keyword, desc, data):
    data = json.dumps({
        'title': '%s - %s' % (keyword, desc),
        'topics': data,
        'currentUser': {}
    })

    templatefilename = visual_file('template.html')

    with open(templatefilename, 'r', encoding='utf-8') as templatefile:
        template = templatefile.read()

    data = re_sub_literal(r'var data =(.*)', 'var data = ' + data, template)

    reportfilename = report_file('ldavisual-%s-%s.html' % (keyword, desc))

    with open(reportfilename, 'w', encoding='utf-8') as reportfile:
        reportfile.write(data)


def visualization_twlda(keyword, desc, encoding='utf-8'):
    cl.section('Twitter-LDA Visualization')

    user_topic = parse_user_topic(desc, encoding=encoding)
    topic_words = parse_topic_words(desc, encoding=encoding)
    result = organize_data('test', user_topic, topic_words)
    export_html(keyword, desc, result)
