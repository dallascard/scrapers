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
    parser.add_option('--first', type=int, default=0,
                      help='First batch: default=%default')
    parser.add_option('--last', type=int, default=0,
                      help='Last batch: default=%default')
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite: default=%default')
    parser.add_option('--overwrite-index', action="store_true", default=False,
                      help='Overwrite index of json objects: default=%default')
    parser.add_option('--log-file', type=str, default='errors.log',
                      help='Log file: default=%default')

    (options, args) = parser.parse_args()

    outdir = args[0]

    start_date = options.start_date
    first = options.first
    last = options.last
    overwrite = options.overwrite
    overwrite_index = options.overwrite_index
    log_file = options.log_file

    with open(log_file, 'w') as f:
        f.write('')

    year = int(start_date[:4])
    month = int(start_date[4:6])
    day = int(start_date[6:8])
    print("Using start date", year, month, day)
    start_date = dt.date(year=year, month=month, day=day)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    target = 'https://chroniclingamerica.loc.gov/batches.json'

    index_file = os.path.join(outdir, 'index.json')
    if overwrite_index or not os.path.exists(index_file):
        download(target, index_file)

    with open(index_file, 'r') as f:
        print("Loading index file")
        data = json.load(f)

    batches = data['batches']
    print(len(batches))

    for batch in tqdm(batches[first:last]):
        batch_name = batch['name']
        batch_url = batch['url']
        page_count = batch['page_count']
        lccns = batch['lccns']
        timestamp = batch['ingested']
        year = int(timestamp[:4])
        month = int(timestamp[5:7])
        day = int(timestamp[8:10])
        date = dt.date(year=year, month=month, day=day)
        if date >= start_date:
            batch_dir = os.path.join(outdir, 'batches', batch_name)
            if not os.path.exists(batch_dir):
                os.makedirs(batch_dir)

            for lccn in lccns:
                outfile = os.path.join(batch_dir, lccn + '.json')
                lccn_url = 'https://chroniclingamerica.loc.gov/lccn/' + lccn + '.json'
                if overwrite or not os.path.exists(outfile):
                    print("Downloading", lccn_url, "to", outfile)
                    download(lccn_url, outfile)

            outfile = os.path.join(batch_dir, 'index.json')
            if overwrite or not os.path.exists(outfile):
                print("Downloading", batch_url, "to", outfile, '(page_count=', str(page_count) + ')')
                download(batch_url, outfile)

            with open(outfile, 'r') as f:
                batch_index = json.load(f)

            issues = batch_index['issues']
            print(len(issues), 'issues')
            for i, issue in enumerate(issues):
                issue_url = issue['url']
                issue_date = issue['date_issued']
                parts = issue_url.split('/')
                lccn_index = parts.index('lccn')
                issue_dir = os.path.join(batch_dir, '/'.join(parts[lccn_index+1:-1]) + '/')
                # drop .json extension
                edition = '.'.join(parts[-1].split('.')[:-1])
                print("making", issue_dir)
                os.makedirs(issue_dir, exist_ok=True)
                outfile = os.path.join(issue_dir, parts[-1])
                if overwrite or not os.path.exists(outfile):
                    print("Downloading", issue_url, "to", outfile, issue_date)
                    download(issue_url, outfile)

                if not os.path.exists(outfile):
                    print(outfile, "not found")
                    with open(log_file, 'a') as f:
                        f.write(outfile + 'not found (from' + issue_url + ').\n')

                else:
                    with open(outfile, 'r') as f:
                        issue = json.load(f)

                    pages = issue['pages']
                    pages_dir = os.path.join(issue_dir, edition + '_pages')
                    if not os.path.exists(pages_dir):
                        os.makedirs(pages_dir)
                    for page in pages:
                        page_url = page['url']
                        page_parts = page_url.split('/')
                        outfile = os.path.join(pages_dir, page_parts[-1])
                        if overwrite or not os.path.exists(outfile):
                            print("Downloading", page_url, "to", outfile)
                            download(page_url, outfile)

                        with open(outfile, 'r') as f:
                            page = json.load(f)

                        # drop .json extension
                        seq_name = '.'.join(page_parts[-1].split('.')[:-1])
                        text_url = page['text']
                        outfile = os.path.join(pages_dir, seq_name + '.txt')
                        if overwrite or not os.path.exists(outfile):
                            print("Downloading", text_url, "to", outfile)
                            download(text_url, outfile)


if __name__ == '__main__':
    main()
