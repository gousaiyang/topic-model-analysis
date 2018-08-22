import csv

import colorlabels as cl
from decouple import config

CSV_FIELD_SIZE_LIMIT = config('CSV_FIELD_SIZE_LIMIT', cast=int)


def csv_reader(csvfilename, encoding='utf-8'):
    csv.field_size_limit(CSV_FIELD_SIZE_LIMIT)

    with open(csvfilename, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            yield row


def export_csv(data, outfilename, encoding='utf-8'):
    cl.progress('Exporting data to csv file: %s' % outfilename)

    it = iter(data)
    num_records = 0

    try:
        first_item = next(it)
    except StopIteration:
        cl.warning('Empty data. Export aborted.')
        return
    else:
        num_records += 1

    with open(outfilename, 'w', newline='', encoding=encoding) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=first_item.keys())
        writer.writeheader()
        writer.writerow(first_item)

        try:
            for item in it:
                num_records += 1
                writer.writerow(item)
        except KeyboardInterrupt:
            cl.warning('User hit Ctrl-C, flushing data...')

    cl.success('%d record(s) saved to csv file.' % num_records)
