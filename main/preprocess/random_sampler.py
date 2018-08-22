import random

import colorlabels as cl

from util import (csv_reader, data_source_file, export_csv,
                  name_with_title_suffix)


def random_sampler(csvfilename, amount):
    cl.section('Data Random Sampler')
    cl.info('Random sampling file: %s' % csvfilename)
    cl.info('Amount: %d' % amount)

    csvfilename = data_source_file(csvfilename)
    data = list(csv_reader(csvfilename))

    random.shuffle(data)
    data = data[:amount]

    exportfilename = name_with_title_suffix(csvfilename, '-sample-%d' % amount)
    export_csv(data, exportfilename)
