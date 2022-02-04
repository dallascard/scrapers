import os
import json
import shutil
import datetime as dt
from glob import glob
from optparse import OptionParser
from collections import defaultdict, Counter
from subprocess import run

from tqdm import tqdm
from common.requests_get import download, get


# Download the index file for OCR batches, and write a bash script to download using wget

def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='/u/scr/dcard/data/chron_am',
                      help='Base directory: default=%default')
    parser.add_option('--start-date', type=str, default='17000101',
                      help='Start downloading from this date: default=%default')
    parser.add_option('--start', type=int, default=0,
                      help='First file: default=%default')
    parser.add_option('--end', type=int, default=10,
                      help='Last file: default=%default')
    #parser.add_option('--sha1-dir', type=str, default=None,
    #                  help='If given, skip files with existing sha1 files in this dir: default=%default')
    parser.add_option('--overwrite-index', action="store_true", default=False,
                      help='Overwrite index of json objects: default=%default')

    (options, args) = parser.parse_args()

    basedir = options.basedir
    start_date = options.start_date
    start = options.start
    end = options.end
    overwrite_index = options.overwrite_index

    year = int(start_date[:4])
    month = int(start_date[4:6])
    day = int(start_date[6:8])
    print("Using start date", year, month, day)
    start_date = dt.date(year=year, month=month, day=day)

    tar_files_dir = os.path.join(basedir, 'tar_files')
    untarred_dir = os.path.join(basedir, 'untarred')
    indexed_dir = os.path.join(basedir, 'indexed')

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

    for i, item in enumerate(items[start:end+1]):
        url = item['url']
        filename = item['name']
        timestamp = item['created']
        year = int(timestamp[:4])
        month = int(timestamp[5:7])
        day = int(timestamp[8:10])
        size = int(item['size'])
        print(i+start, url, filename, size)
        date = dt.date(year=year, month=month, day=day)
        #if sha1_dir is not None and os.path.exists(os.path.join(sha1_dir, filename + '.sha1')):
        #    print("Skipping", url, "with existing sha1")
        tarfile = os.path.join(tar_files_dir, filename)
        if date >= start_date and not os.path.exists(tarfile):
            command = ['wget', url, '-P', tar_files_dir]
            print(' '.join(command))
            run(command)
        else:
            print("Skipping", url, 'download')

        # Do untar
        if os.path.exists(tarfile):
            file_size = os.path.getsize(tarfile)
            try:
                assert file_size == size
                print("File size is as expected")
            except AssertionError as e:
                print(tarfile)
                print("File size (actual):", file_size)
                print("File size expected:", size)
                raise e

            command = ['tar', '-xvf', tarfile, '--wildcards', "*.txt", '-C', untarred_dir]
            print(' '.join(command))
            #run(command)
            raise RuntimeError('test')

        else:
            raise FileNotFoundError("tarfile not found:", tarfile)

        print("Deleting tar file")
        os.remove(tarfile)

        # Index files
        # path = tar_file_dir/year/month/day/
        print("Reading and indexing files")
        docs_by_paper = defaultdict(list)
        files = sorted(glob(os.path.join(untarred_dir, '*', '*', '*', 'ed-*', 'seq-*', 'ocr.txt')))
        for infile in files:
            parts = infile.split('/')
            seq = parts[-2]
            ed = parts[-3]
            day = parts[-4]
            month = parts[-5]
            year = parts[-6]
            paper = parts[-7]
            text = f.read().strip()
            if len(text) > 0:
                docs_by_paper[paper].append({'y': year, 'm': month, 'd': day, 'e': ed, 's': seq, 't': text})

        # Update indices
        if len(docs_by_paper) > 0:
            for source, lines in docs_by_paper.items():
                print("Saving index for", source)
                outfile = os.path.join(indexed_dir, source + '.jsonlist')
                with open(outfile, 'a') as f:
                    for line in lines:
                        f.write(json.dumps(line) + '\n')

        print("Cleaning up")
        shutil.rmtree(os.path.join(untarred_dir, '*'))


if __name__ == '__main__':
    main()
