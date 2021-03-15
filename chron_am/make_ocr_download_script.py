import os
import json
import datetime as dt
from glob import glob
from optparse import OptionParser
from collections import defaultdict, Counter

from tqdm import tqdm
from common.requests_get import download, get


# Download the index file for OCR batches, and write a bash script to download using wget

def main():
    usage = "%prog outdir"
    parser = OptionParser(usage=usage)
    parser.add_option('--start-date', type=str, default='17000101',
                      help='Start downloading from this date: default=%default')
    parser.add_option('--start', type=int, default=0,
                      help='First file: default=%default')
    parser.add_option('--end', type=int, default=10,
                      help='Last file: default=%default')
    parser.add_option('--sha1-dir', type=str, default=None,
                      help='If given, skip files with existing sha1 files in this dir: default=%default')
    parser.add_option('--overwrite-index', action="store_true", default=False,
                      help='Overwrite index of json objects: default=%default')

    (options, args) = parser.parse_args()

    outdir = args[0]

    start_date = options.start_date
    start = options.start
    end = options.end
    sha1_dir = options.sha1_dir
    overwrite_index = options.overwrite_index

    sha1_files = set()
    if sha1_dir is not None:
        files = glob(os.path.join(sha1_dir, '*.sha1'))
        sha1_files = set([os.path.basename(f) for f in files])
        print("Found {:d} sha1 files".format(len(sha1_files)))

    year = int(start_date[:4])
    month = int(start_date[4:6])
    day = int(start_date[6:8])
    print("Using start date", year, month, day)
    start_date = dt.date(year=year, month=month, day=day)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    target = 'https://chroniclingamerica.loc.gov/ocr.json'

    index_file = os.path.join(outdir, 'index.json')
    if overwrite_index or not os.path.exists(index_file):
        download(target, index_file)

    with open(index_file, 'r') as f:
        data = json.load(f)

    items = data['ocr']
    print(len(items))

    outlines = []

    for item in tqdm(items[start:end]):
        url = item['url']
        filename = item['name']
        timestamp = item['created']
        year = int(timestamp[:4])
        month = int(timestamp[5:7])
        day = int(timestamp[8:10])
        size = item['size']
        date = dt.date(year=year, month=month, day=day)
        if sha1_dir is not None and os.path.exists(os.path.join(sha1_dir, filename + '.sha1')):
            print("Skipping", url, "with existing sha1")
        elif date >= start_date and not os.path.exists(os.path.join(outdir, filename)):
            print("Adding", url, filename, size)
            outlines.append('wget ' + url + '\n')
        else:
            print("Skipping", url)

    print("Added {:d} files in total".format(len(outlines)))
    outfile = os.path.join(outdir, 'download_' + str(start_date) + '_' + str(start) + '-' + str(end) + '.sh')
    with open(outfile, 'w') as f:
        for line in outlines:
            f.write(line)


if __name__ == '__main__':
    main()
