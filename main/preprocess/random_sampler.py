import csv
import random

import colorlabels as cl

from util import (data_source_file, export_csv, name_with_title_suffix,
                  set_csv_field_size_limit)


def random_sampler(csvfilename, amount):
    cl.section('Data Random Sampler')
    cl.info('Random sampling file: %s' % csvfilename)
    cl.info('Amount: %d' % amount)

    csvfilename = data_source_file(csvfilename)

    set_csv_field_size_limit()

    with open(csvfilename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]

    random.shuffle(data)
    data = data[:amount]

    exportfilename = name_with_title_suffix(csvfilename, '-sample-%d' % amount)
    export_csv(data, exportfilename)
