import os
import json
import datetime as dt
from optparse import OptionParser
from collections import defaultdict, Counter

from tqdm import tqdm
from common.requests_get import download, get


def main():
    usage = "%prog outdir"
    parser = OptionParser(usage=usage)
    parser.add_option('--start-date', type=str, default='2021015',
                      help='Start downloading from this date: default=%default')
    parser.add_option('--max-files', type=int, default=10,
                      help='Limit the number of files to download: default=%default')
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite data files: default=%default')
    parser.add_option('--overwrite-index', action="store_true", default=False,
                      help='Overwrite index of json objects: default=%default')

    (options, args) = parser.parse_args()

    outdir = args[0]

    start_date = options.start_date
    max_files = options.max_files
    overwrite = options.overwrite
    overwrite_index = options.overwrite_index

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
        data = get(target, html_only=False)
        if data is None:
            raise RuntimeError("Index file not downloaded")
        else:
            with open(index_file, 'w') as f:
                json.dump(data, f)
    else:
        with open(index_file) as f:
            data = json.load(f)

    items = data['ocr']

    count = 0
    for item in tqdm(items):
        url = item['url']
        filename = item['name']
        timestamp = item['created']
        year = int(timestamp[:4])
        month = int(timestamp[5:7])
        day = int(timestamp[8:10])
        date = dt.date(year=year, month=month, day=day)
        if date >= start_date:
            outfile = os.path.join(outdir, filename)
            if overwrite or not os.path.exists(outfile):
                print("Downloading", url, "to", outfile)
                download(url, outfile, binary=True, stream=True)
                count += 1
            else:
                print("Skipping", outfile)
        else:
            print("Skipping", filename, ":", date, "after", start_date)
        if count >= max_files:
            break


if __name__ == '__main__':
    main()
