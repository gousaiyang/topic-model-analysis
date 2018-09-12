import os
import re
import subprocess

import colorlabels as cl

from util import (TWLDA_BASE_DIR, TimeMeasure, escape_param, is_windows,
                  redirect_command, tee_command, twlda_base_file,
                  twlda_data_file, twlda_result_file)

SEP = ';' if is_windows else ':'
CLASSPATH = SEP.join(map(twlda_base_file, ['bin', 'lib/args4j-2.0.6.jar',
                                                  'lib/jargs.jar',
                                                  'lib/TwitterTokenizer.jar']))
COMMAND = 'java -cp %s TwitterLDA.TwitterLDAmain' % escape_param(CLASSPATH)
LOGFILE = 'twlda-output.log'


def set_parameters(topics, alpha_g, beta_word, beta_b, gamma, iteration):
    parameters_filename = twlda_data_file('modelParameters-test.txt')

    with open(parameters_filename, 'w', encoding='utf-8') as pf:
        pf.write('topics: %d\n' % topics)
        pf.write('alpha_g: %f\n' % alpha_g)
        pf.write('beta_word: %f\n' % beta_word)
        pf.write('beta_b: %f\n' % beta_b)
        pf.write('gamma: %f\n' % gamma)
        pf.write('iteration: %d\n' % iteration)


def run_twlda(show_console_output):
    command_wrapper = tee_command if show_console_output else redirect_command
    subprocess.call(command_wrapper(COMMAND, LOGFILE), cwd=str(TWLDA_BASE_DIR))


def move_result(output_desc):
    os.rename(twlda_result_file('test'), twlda_result_file(output_desc))
    os.rename(twlda_base_file(LOGFILE),
              twlda_result_file('%s/%s' % (output_desc, LOGFILE)))


def twitter_lda(*, output_desc, topics, iteration, alpha_g=None,
                beta_word=0.01, beta_b=0.01, gamma=20,
                show_console_output=True):
    cl.section('Twitter-LDA Runner')
    cl.info('Output description: %s' % output_desc)

    assert re.fullmatch(r'[-_0-9a-zA-Z]+', output_desc)

    if alpha_g is None:
        alpha_g = 50 / topics

    set_parameters(topics, alpha_g, beta_word, beta_b, gamma, iteration)

    with TimeMeasure('Twitter-LDA training'):
        run_twlda(show_console_output=show_console_output)

    move_result(output_desc)
