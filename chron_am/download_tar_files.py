import os
import json
import shutil
import datetime as dt
from glob import glob
from optparse import OptionParser
from collections import defaultdict, Counter
from subprocess import run

from tqdm import tqdm
import pandas as pd
from common.requests_get import download, get


# Download the index file for OCR batches, and write a bash script to download using wget

def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='/u/scr/dcard/data/chron_am',
                      help='Base directory: default=%default')
    #parser.add_option('--logfile', type=str, default='errors.txt',
    #                  help='Logfile location (in basedir): default=%default')
    parser.add_option('--start-date', type=str, default='17000101',
                      help='Start downloading from this date (for getting updates): default=%default')
    parser.add_option('--start', type=int, default=0,
                      help='First file: default=%default')
    parser.add_option('--end', type=int, default=1,
                      help='Last file: default=%default')
    #parser.add_option('--sha1-dir', type=str, default=None,
    #                  help='If given, skip files with existing sha1 files in this dir: default=%default')
    parser.add_option('--overwrite-index', action="store_true", default=False,
                      help='Overwrite index of json objects: default=%default')
    parser.add_option('--skip-untar', action="store_true", default=False,
                      help='Skip untar: default=%default')
    parser.add_option('--skip-size-check', action="store_true", default=False,
                      help='Skip checking for file size agreement: default=%default')

    (options, args) = parser.parse_args()

    basedir = options.basedir
    #error_log = os.path.join(basedir, options.logfile)
    start_date = options.start_date
    start = options.start
    end = options.end
    overwrite_index = options.overwrite_index
    skip_untar = options.skip_untar
    skip_size_check = options.skip_size_check

    year = int(start_date[:4])
    month = int(start_date[4:6])
    day = int(start_date[6:8])
    print("Using start date", year, month, day)
    start_date = dt.date(year=year, month=month, day=day)

    tar_files_dir = os.path.join(basedir, 'tar_files')
    untarred_dir = os.path.join(basedir, 'untarred')
    indexed_dir = os.path.join(basedir, 'indexed')
    logfile = os.path.join(basedir, 'log.csv')

    if os.path.exists(logfile):
        log_df = pd.read_csv(logfile, header=0, index_col=0)
    else:
        log_df = pd.DataFrame(columns=['id', 'datetime', 'index', 'filename', 'url', 'action', 'checksum'])

    current_id = len(log_df)

    for dir in [basedir, tar_files_dir, untarred_dir, indexed_dir]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    target = 'https://chroniclingamerica.loc.gov/ocr.json'

    index_file = os.path.join(basedir, 'index.json')
    if overwrite_index or not os.path.exists(index_file):
        download(target, index_file)

    with open(index_file, 'r') as f:
        data = json.load(f)

    items = data['ocr']
    print(len(items))

    log_rows = []

    for i, item in enumerate(items[start:end]):
        index = start+i
        url = item['url']
        filename = item['name']
        timestamp = item['created']
        year = int(timestamp[:4])
        month = int(timestamp[5:7])
        day = int(timestamp[8:10])
        sha1 = item['sha1']
        size = int(item['size'])
        print(i+start, url, filename, size)
        date = dt.date(year=year, month=month, day=day)
        #if sha1_dir is not None and os.path.exists(os.path.join(sha1_dir, filename + '.sha1')):
        #    print("Skipping", url, "with existing sha1")
        tarfile = os.path.join(tar_files_dir, filename)
        logfile = tarfile + '.log'
        if date < start_date:
            print("Skipping download of file {:s} from before".format(filename), start_date)
            log_rows.append([current_id, str(dt.datetime.now()), index, filename, url, 'skipped', None])
        else:
            command = ['wget', url, '-P', tar_files_dir]
            print("Downloading from", url)
            print(' '.join(command))
            run(command)

            # compute checksum
            print("Computing checksum")
            tar_file = os.path.join(tar_files_dir, filename)
            command = ['sha1sum', tar_file, '>', tar_file + '.sha1']
            print(' '.join(command))
            run(command)

            # compare checksums
            print("Comparing checksum")
            with open(tar_file + '.sha1') as f:
                checksum = f.read()
            checksum = checksum.strip()
            
            if checksum == sha1:
                print("Checksum passed")
                log_rows.append([current_id, str(dt.datetime.now()), index, filename, url, 'downloaded', 'passed'])
            else:
                print("Checksum failed")
                log_rows.append([current_id, str(dt.datetime.now()), index, filename, url, 'downloaded', 'failed'])

        current_id += 1

    temp_df = pd.DataFrame(log_rows)
    log_df = pd.concat([log_df, temp_df])
    log_df.to_csv(logfile)


if __name__ == '__main__':
    main()
