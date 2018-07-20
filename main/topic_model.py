import json
import os
import re
import time
import webbrowser
from urllib.request import pathname2url

import colorlabels as cl
import pyLDAvis
import pyLDAvis.gensim
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from gensim.models.ldamulticore import LdaMulticore

from util import TimeMeasure, data_source_file, model_file, report_file

N_WORKERS = os.cpu_count()


def open_html_in_browser(filename):
    webbrowser.open('file:' + pathname2url(os.path.abspath(filename)))


def measure_coherence(model, texts, corpus, dictionary):
    cm = CoherenceModel(model=model, corpus=corpus, dictionary=dictionary,
                        coherence='u_mass')
    u_mass = cm.get_coherence()

    cm = CoherenceModel(model=model, texts=texts, dictionary=dictionary,
                        coherence='c_v')
    c_v = cm.get_coherence()

    cm = CoherenceModel(model=model, texts=texts, dictionary=dictionary,
                        coherence='c_uci')
    c_uci = cm.get_coherence()

    cm = CoherenceModel(model=model, texts=texts, dictionary=dictionary,
                        coherence='c_npmi')
    c_npmi = cm.get_coherence()

    cl.info('Topic coherence: u_mass = %f, c_v = %f, c_uci = %f, c_npmi = %f'
            % (u_mass, c_v, c_uci, c_npmi))


def lda_topic_model(input_filename, keyword, size, *,
                    num_topics, iterations=50, passes=1):
    cl.section('LDA Topic Model Training')
    cl.info('Keyword: %s' % keyword)
    cl.info('Data size: %d' % size)
    cl.info('Number of topics: %d' % num_topics)
    cl.info('Iterations: %d' % iterations)
    cl.info('Passes: %d' % passes)

    assert re.fullmatch(r'[-_0-9a-zA-Z+]+', keyword)

    input_filename = data_source_file(input_filename)

    with TimeMeasure('load_preprocessed_text'):
        with open(input_filename, 'r', encoding='utf-8') as infile:
            preprocessed_texts = json.load(infile)

    with TimeMeasure('gen_dict_corpus'):
        cl.progress('Generating dictionary and corpus...')
        dictionary = Dictionary(preprocessed_texts)
        corpus = [dictionary.doc2bow(text) for text in preprocessed_texts]

    with TimeMeasure('training'):
        cl.progress('Performing training...')
        ldamodel = LdaMulticore(corpus, workers=N_WORKERS, id2word=dictionary,
                                num_topics=num_topics, iterations=iterations,
                                passes=passes,
                                alpha='symmetric', eta='auto')  # Other params?
        cl.success('Training finished.')

    description = '%s-%d-%d-%dx%d-%s' % (keyword, size, num_topics, iterations,
                                         passes, time.strftime('%Y%m%d%H%M%S'))

    with TimeMeasure('save_model'):
        modelfilename = 'ldamodel-%s' % description
        ldamodel.save(model_file(modelfilename))
        cl.success('Model saved as: %s' % modelfilename)

    with TimeMeasure('measure_coherence'):
        cl.progress('Measuring topic coherence...')
        measure_coherence(ldamodel, preprocessed_texts, corpus, dictionary)

    with TimeMeasure('vis_save'):
        cl.progress('Preparing visualization...')
        vis = pyLDAvis.gensim.prepare(ldamodel, corpus, dictionary)
        htmlfilename = 'ldavis-%s.html' % description
        htmlfilename = report_file(htmlfilename)
        pyLDAvis.save_html(vis, htmlfilename)
        cl.success('Visualized result saved in file: %s' % htmlfilename)

    open_html_in_browser(htmlfilename)
