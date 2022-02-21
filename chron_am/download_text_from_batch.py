import os
import json
import datetime as dt
from optparse import OptionParser
from collections import defaultdict, Counter

from tqdm import tqdm
from common.requests_get import download, get


# Download text files from batches of Chronicling Ameirca
# WARNING: SLOW! use make_download_ocr_script.py instead!

def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--batch-file', type=str, default='/u/scr/dcard/data/chron_am/extra_jsons/filename.json',
                      help='Batch file to process (from check_batches.py): default=%default')
    #parser.add_option('--first', type=int, default=0,
    #                  help='First batch: default=%default')
    #parser.add_option('--last', type=int, default=0,
    #                 help='Last batch: default=%default')
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite: default=%default')
    #parser.add_option('--overwrite-index', action="store_true", default=False,
    #                  help='Overwrite index of json objects: default=%default')
    #parser.add_option('--log-file', type=str, default='errors.log',
    #                  help='Log file: default=%default')

    (options, args) = parser.parse_args()

    batch_file = options.batch_file
    #start_date = options.start_date
    #first = options.first
    #last = options.last
    overwrite = options.overwrite
    #overwrite_index = options.overwrite_index
    #log_file = options.log_file

    #with open(log_file, 'w') as f:
    #    f.write('')


    temp_dir, basename = os.path.splitext(batch_file)
    json_dir = os.path.join(temp_dir, 'downloads')
    text_dir = os.path.join(temp_dir, 'text')

    print(temp_dir)

    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    if not os.path.exists(text_dir):
        os.makedirs(text_dir)

    with open(batch_file, 'r') as f:
        data = json.load(f)

    batches = data['batches']
    print(len(batches))

    for batch in tqdm(batches):
        batch_name = batch['name']
        batch_url = batch['url']
        page_count = batch['page_count']
        lccns = batch['lccns']
        timestamp = batch['ingested']
        issues = batch['issues']


        #for lccn in lccns:
        #    outfile = os.path.join(json_dir, lccn + '.json')
        #    lccn_url = 'https://chroniclingamerica.loc.gov/lccn/' + lccn + '.json'
        #    if overwrite or not os.path.exists(outfile):
        #        print("Downloading", lccn_url, "to", outfile)
        #        download(lccn_url, outfile)

        #outfile = os.path.join(batch_dir, 'index.json')
        #if overwrite or not os.path.exists(outfile):
        #    print("Downloading", batch_url, "to", outfile, '(page_count=', str(page_count) + ')')
        #    download(batch_url, outfile)

        #with open(outfile, 'r') as f:
        #    batch_index = json.load(f)

        print(len(issues), 'issues')
        for i, issue in enumerate(issues):
            issue_url = issue['url']
            issue_date = issue['date_issued']
            parts = issue_url.split('/')
            lccn_index = parts.index('lccn')
            issue_dir = os.path.join(text_dir, '/'.join(parts[lccn_index+1:-1]) + '/')
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
                #with open(log_file, 'a') as f:
                #    f.write(outfile + 'not found (from' + issue_url + ').\n')

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
