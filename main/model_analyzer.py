import collections
import csv
import json

import colorlabels as cl
from gensim.models.ldamulticore import LdaMulticore

from util import (TimeMeasure, data_source_file, model_file, rank, report_file,
                  set_csv_field_size_limit)


def load_all(modeldesc, sourcedesc):
    modelfilename = model_file('ldamodel-%s' % modeldesc)
    ldamodel = LdaMulticore.load(modelfilename)

    corpusfilename = model_file('ldacorpus-%s.json' % modeldesc)
    with open(corpusfilename, 'r', encoding='utf-8') as corpusfile:
        corpus = json.load(corpusfile)

    prepfilename = data_source_file(sourcedesc + '.prep.json')
    with open(prepfilename, 'r', encoding='utf-8') as prepfile:
        prep_items = json.load(prepfile)

    set_csv_field_size_limit()

    sourcefilename = data_source_file(sourcedesc + '.csv')
    with open(sourcefilename, newline='', encoding='utf-8') as sourcefile:
        reader = csv.DictReader(sourcefile)
        source_texts = {row['id']: row['text'] for row in reader}

    return ldamodel, corpus, prep_items, source_texts


def get_topic_words(ldamodel, topic_id, topn=30, sep=' '):
    topics = ldamodel.show_topic(topic_id, topn=topn)
    return sep.join(t[0] for t in topics)


def get_topic_top_docs(topic_docs, num_top_docs, prep_ids, source_texts):
    topic_docs_l = ((k, v) for k, v in topic_docs.items())
    topic_docs_l = sorted(topic_docs_l, key=lambda x: x[1], reverse=True)
    topic_docs_l = topic_docs_l[:num_top_docs]
    topic_docs = (source_texts[prep_ids[t[0]]] for t in topic_docs_l)
    return topic_docs


def export_markdown(modeldesc, sourcedesc, topics):
    analysisfilename = report_file('ldaanl-%s.md' % modeldesc)

    with open(analysisfilename, 'w', encoding='utf-8') as analysisfile:
        analysisfile.write('# Topic Model Analysis\n\n')
        analysisfile.write('- Model description: %s\n' % modeldesc)
        analysisfile.write('- Source description: %s\n' % sourcedesc)

        for index, topic in enumerate(topics):
            analysisfile.write('\n## %s Topic\n\n' % rank(index + 1))
            analysisfile.write('ID: %d\n\n' % topic['topic_id'])
            analysisfile.write('Words: %s\n\n' % topic['words'])

            for text in topic['documents']:
                text = text.strip()
                analysisfile.write('- %s\n' % text)

    cl.success('Analysis file saved as: %s' % analysisfilename)


def model_analyzer(modeldesc, sourcedesc, *, num_top_words=30,
                   num_top_docs=30, debug=False):
    cl.section('LDA Model Analyzer')
    cl.info('Model description: %s' % modeldesc)
    cl.info('Source description: %s' % sourcedesc)

    with TimeMeasure('load_all'):
        ldamodel, corpus, prep_items, source_texts = load_all(modeldesc,
                                                              sourcedesc)

    with TimeMeasure('analyzing'):
        prep_ids = tuple(item[0] for item in prep_items)
        dictionary = ldamodel.id2word
        num_topics = ldamodel.num_topics
        topics = [{
                    'topic_id': i,
                    'words': get_topic_words(ldamodel, i, num_top_words),
                    'popularity': 0.0,
                    'documents': collections.defaultdict(float)
                } for i in range(num_topics)]

        if debug:
            debugfilename = model_file('ldadoctopics-%s.txt' % modeldesc)
            with open(debugfilename, 'w', encoding='utf-8') as debugfile:
                for index, doc in enumerate(corpus):
                    text_id = prep_ids[index]
                    doc_topics = ldamodel.get_document_topics(doc)
                    text = source_texts[text_id].strip()
                    debugfile.write('%s -> %r, %s\n' % (text_id, doc_topics,
                                                        text))

        term_topics_cache = {}

        for word in dictionary:
            term_topics_cache[word] = ldamodel.get_term_topics(word)

        for index, doc in enumerate(corpus):
            for topic_id, prob in ldamodel.get_document_topics(doc):
                topics[topic_id]['popularity'] += prob

            for word, freq in doc:
                if word not in dictionary:
                    continue

                for topic_id, prob in term_topics_cache[word]:
                    topics[topic_id]['documents'][index] += prob * freq

        for topic in topics:
            topic['documents'] = get_topic_top_docs(topic['documents'],
                                                    num_top_docs,
                                                    prep_ids, source_texts)

        topics = sorted(topics, key=lambda x: x['popularity'], reverse=True)

    with TimeMeasure('export_markdown'):
        export_markdown(modeldesc, sourcedesc, topics)
