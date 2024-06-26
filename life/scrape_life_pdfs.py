import os
import json
import time
import datetime as dt
from glob import glob
from optparse import OptionParser
from collections import Counter

import wget


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='/data/dalc/magazines/life/',
                      help='Data directory: default=%default')
    parser.add_option('--first-date', type=str, default='1936-11-23',
                      help='First date: default=%default')
    parser.add_option('--first-volume', type=int, default=1,
                      help='First volume: default=%default')
    parser.add_option('--first-number', type=int, default=1,
                      help='First number: default=%default')
    parser.add_option('--pause', type=int, default=5,
                      help='Pause between issues: default=%default')
    parser.add_option('--with-text', action="store_true", default=False,
                      help='Get the PDFs with text (may be lower quality): default=%default')    
    #parser.add_option('--overwrite', action="store_true", default=False,
    #                  help='Overwrite files: default=%default')
    #parser.add_option('--clear-log', action="store_true", default=False,
    #                  help='Clear log file before starting: default=%default')

    (options, args) = parser.parse_args()

    data_dir = options.basedir
    first_date = options.first_date
    first_volume = options.first_volume
    first_number = options.first_number
    pause = options.pause
    with_text = options.with_text

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    parts = first_date.split('-')
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])
    date = dt.date(year, month, day)
    
    current_month = date.month
    current_year = date.year


    volume = first_volume
    number = first_number

    # start dates:
    # 1936-11-23 v01 n01
    # ... missing several ...
    # 1955-12-26 v40 n01
    # 1956-01-09 v40 n02
    # 1957-01-07 v42 n01
    # 1958-01-06 v44 n01
    # 1959-01-05 v46 n01

    nospace_date = dt.date(1943, 10, 18)
    second_date = dt.date(1950, 1, 2)

    done = False
    while not done:
        date_str = date.strftime('%Y-%m-%d')
        if date < nospace_date or date >= second_date:
            url = 'https://archive.org/download/Life-{:s}-Vol-{:d}-No-{:d}/Life - {:s} - v{:s} n{:s}'.format(date_str, volume, number, date_str, str(volume).zfill(2), str(number).zfill(2))
        else:
            url = 'https://archive.org/download/Life-{:s}-Vol-{:d}-No-{:d}/Life - {:s} - v{:s}n{:s}'.format(date_str, volume, number, date_str, str(volume).zfill(2), str(number).zfill(2))

        if with_text:
            url += '_text.pdf'
            outfile = os.path.join(data_dir, '-'.join([date_str, str(volume), str(number)]) + '_text.pdf')
        else:
            url += '.pdf'
            outfile = os.path.join(data_dir, '-'.join([date_str, str(volume), str(number)]) + '.pdf')       
        
        success = download_file(url, outfile, max_tries=3, overwrite=True)

        if not success:
            print("Failed on", date_str, volume, number)        
            done = True
        
        number += 1
        date += dt.timedelta(days=7)
        # Volume number increases in July and January
        if date.year > current_year:
            volume += 1
            number = 1
        elif date.month == 7 and current_month == 6:
            volume += 1
            number = 1
        current_month = date.month
        current_year = date.year
        
        time.sleep(pause)


def download_file(url, outfile, max_tries=3, logfile=None, overwrite=False):
    tries = 0
    success = False
    if os.path.exists(outfile) and not overwrite:
        print("Skipping {:s}".format(url))
    else:
        if os.path.exists(outfile) and overwrite:
            print("Deleting", outfile)
            os.remove(outfile)
        while tries < max_tries and not success:
            try:
                print("Downloading {:s}".format(url))
                wget.download(url, out=outfile)
                success = True
            except Exception as e:
                print("Download failed on", url)
                if os.path.exists(outfile):
                    os.remove(outfile)
                if tries < max_tries:
                    print("Pausing for 3 seconds...")
                    time.sleep(3)
                    tries += 1
                else:
                    print("Maximum number of tries exceeded on", url)
                    if logfile is not None:
                        with open(logfile, 'a') as f:
                            f.write("Maximum number of tries exceeded on" + url + '\n')
                    raise e
    print()
    return success


if __name__ == '__main__':
    main()
