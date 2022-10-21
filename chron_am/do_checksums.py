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
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite tar files: default=%default')
    #parser.add_option('--skip-untar', action="store_true", default=False,
    #                  help='Skip untar: default=%default')
    #parser.add_option('--skip-size-check', action="store_true", default=False,
    #                  help='Skip checking for file size agreement: default=%default')

    (options, args) = parser.parse_args()



    index_file = os.path.join(basedir, 'index.json')
    with open(index_file, 'r') as f:
        data = json.load(f)

    items = data['ocr']
    print(len(items))


    for i, item in enumerate(items):
        url = item['url']
        filename = item['name']
        sha1 = item['sha1']

        # compute checksum
        print("Computing checksum")
        tar_file = os.path.join(tar_files_dir, filename)
        command = ['sha1sum', tar_file, '>', tar_file + '.sha1']
        print(' '.join(command))
        result = run(command, capture_output=True)

        output = result.stdout
        print(output)
        checksum = output.split()[0].decode("utf-8") 
        print(checksum)

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
