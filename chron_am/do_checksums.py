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
    parser.add_option('--max-files', type=int, default=None,
                      help='Max files to proecss (for debugging): default=%default')
    #parser.add_option('--start-date', type=str, default='17000101',
    #                  help='Start downloading from this date (for getting updates): default=%default')
    #parser.add_option('--start', type=int, default=0,
    #                  help='First file: default=%default')
    #parser.add_option('--end', type=int, default=1,
    #                  help='Last file: default=%default')
    #parser.add_option('--sha1-dir', type=str, default=None,
    #                  help='If given, skip files with existing sha1 files in this dir: default=%default')
    #parser.add_option('--overwrite-index', action="store_true", default=False,
    #                  help='Overwrite index of json objects: default=%default')
    #parser.add_option('--overwrite', action="store_true", default=False,
    #                  help='Overwrite tar files: default=%default')
    #parser.add_option('--skip-untar', action="store_true", default=False,
    #                  help='Skip untar: default=%default')
    #parser.add_option('--skip-size-check', action="store_true", default=False,
    #                  help='Skip checking for file size agreement: default=%default')

    (options, args) = parser.parse_args()

    basedir = options.basedir
    max_files = options.max_files

    tar_files_dir = os.path.join(basedir, 'tar_files')
    checksum_dir = os.path.join(basedir, 'checksums')
    if not os.path.exists(checksum_dir):
        os.makedirs(checksum_dir)

    index_file = os.path.join(basedir, 'index.json')
    with open(index_file, 'r') as f:
        data = json.load(f)

    items = data['ocr']
    print(len(items))

    urls = []
    filenames = []
    missing = []
    sha1s = []
    checksums = []
    mismatches = []

    if max_files is None:
        max_files = len(items)

    for i, item in enumerate(items[:max_files]):
        print("({:d} / {:d})")
        url = item['url']
        filename = item['name']
        sha1 = item['sha1']
        print(filename)

        urls.append(url)
        filenames.append(filename)
        sha1s.append(sha1)

        # compute checksum
        tar_file = os.path.join(tar_files_dir, filename)
        
        if not os.path.exists(tar_file):
            print("File not found:", tar_file)
            missing.append(1)
            checksums.append('')
            mismatches.append('')
        else:
            missing.append(0)
            
            #outfile = os.path.join(checksum_dir, filename + '.sha1')
            command = ['sha1sum', tar_file]
            print(' '.join(command))
            result = run(command, capture_output=True)

            output = result.stdout
            print(output)
            checksum = output.split()[0].decode("utf-8") 
            print(checksum)

            checksums.append(checksum)

            if checksum == sha1:
                mismatches.append(0)
            else:
                print("Checksum failed", filename, sha1, checksum)
                mismatches.append(1)


    df = pd.DataFrame(filenames, columns=['filename'])
    df['url'] = urls
    df['missing'] = missing
    df['sha1'] = sha1s
    df['checksum'] = checksums
    df['mismatch'] = mismatches
    df.to_csv(os.path.join(checksum_dir, 'checksums.csv'))


if __name__ == '__main__':
    main()
