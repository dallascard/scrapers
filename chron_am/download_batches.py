import os
import json
import time
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
    parser.add_option('--end', type=int, default=None,
                      help='Last file: default=%default')
    #parser.add_option('--sha1-dir', type=str, default=None,
    #                  help='If given, skip files with existing sha1 files in this dir: default=%default')
    parser.add_option('--pause', type=int, default=9,
                      help='Time to wait on error: default=%default')
    parser.add_option('--overwrite-index', action="store_true", default=False,
                      help='Overwrite index of json objects: default=%default')
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite tar files: default=%default')
    #parser.add_option('--skip-untar', action="store_true", default=False,
    #                  help='Skip untar: default=%default')
    #parser.add_option('--skip-size-check', action="store_true", default=False,
    #                  help='Skip checking for file size agreement: default=%default')

    (options, args) = parser.parse_args()

    basedir = options.basedir
    #error_log = os.path.join(basedir, options.logfile)
    start_date = options.start_date
    start = options.start
    end = options.end
    pause = options.pause
    overwrite_index = options.overwrite_index
    overwrite = options.overwrite

    year = int(start_date[:4])
    month = int(start_date[4:6])
    day = int(start_date[6:8])
    print("Using start date", year, month, day)
    start_date = dt.date(year=year, month=month, day=day)

    tar_files_dir = os.path.join(basedir, 'tar_files')
    if not os.path.exists(tar_files_dir):
        os.makedirs(tar_files_dir)

    target = 'https://chroniclingamerica.loc.gov/ocr.json'

    index_file = os.path.join(basedir, 'index.json')
    if overwrite_index or not os.path.exists(index_file):
        download(target, index_file)

    with open(index_file, 'r') as f:
        data = json.load(f)

    items = data['ocr']
    print(len(items))

    if end is None:
        end = len(items)

    for i, item in enumerate(items[start:end]):
        index = start+i
        url = item['url']
        filename = item['name']
        timestamp = item['created']
        year = int(timestamp[:4])
        month = int(timestamp[5:7])
        day = int(timestamp[8:10])
        #sha1 = item['sha1']
        size = int(item['size'])
        print(index, url, filename, size)
        date = dt.date(year=year, month=month, day=day)
        #if sha1_dir is not None and os.path.exists(os.path.join(sha1_dir, filename + '.sha1')):
        #    print("Skipping", url, "with existing sha1")
        tarfile = os.path.join(tar_files_dir, filename)
        if date < start_date:
            print("Skipping download of file {:s} from before".format(filename), start_date)
        elif os.path.exists(tarfile) and not overwrite:
            print("Skipping download of existing file {:s}".format(filename))
        else:
            attempts = 0
            destination_file = os.path.join(tar_files_dir, filename)
            while not os.path.exists(destination_file):
                command = ['wget', url, '-P', tar_files_dir]
                print("Downloading from", url, "(attempt {:d}".format(attempts))
                print(' '.join(command))
                run(command)            
                
                if not os.path.exists(destination_file):
                    print("** ERROR **: File not downloaded:", destination_file)
                    print("Sleeping for 180 seconds")
                    time.sleep(180)

                elif os.path.getsize(destination_file) == 0:
                    raise RuntimeError("** ERROR **: Empty file:", destination_file)
                
                attempts += 1

                if attempts >= 10:
                    raise RuntimeError("Failed 10 times on", url)
        
            print("Pausing for {:d} seconds".format(pause))
            time.sleep(pause)

if __name__ == '__main__':
    main()
