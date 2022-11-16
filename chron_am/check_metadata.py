import os
import gzip
import json
import time
from glob import glob
from subprocess import run
from optparse import OptionParser
from collections import defaultdict, Counter

import numpy as np
import pandas as pd
from tqdm import tqdm

from common.requests_get import download


# This script should compare the metadata against the downloaded articles

def main():
    usage = "%prog basedir"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='/u/scr/dcard/data/chron_am',
                      help='Base directory: default=%default')
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    basedir = options.basedir

    text_dir = os.path.join(basedir, 'text_only')
    metadata_dir = os.path.join(basedir, 'metadata')
    seqs_dir = os.path.join(basedir, 'seq_counts')
    if not os.path.exists(seqs_dir):
        os.makedirs(seqs_dir)
    
    files = sorted(glob(os.path.join(text_dir, '*.gz')))

    articles_by_lccn = defaultdict(set)
    seq_counts = defaultdict(Counter)

    print("Reading articlse")
    for infile in tqdm(files):
        with gzip.open(infile, 'rt') as f:
            lines = f.readlines()
        for line in lines:
            line = json.loads(line)
            lccn = line['sn']
            year = line['year']
            month = line['month']
            day = line['day']
            ed = line['ed']
            seq = line['seq']
            key = str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + '-' + str(ed)
            articles_by_lccn[lccn].add(key)
            seq_counts[lccn][key] += 1

    metadata_by_lccn = defaultdict(set)
    
    urls_by_key = defaultdict(list)

    print("Reading metadata")
    files = sorted(glob(os.path.join(metadata_dir, '*.json')))
    for infile in tqdm(files):
        with open(infile) as f:
            metadata = json.load(f)
        lccn = metadata['lccn']
        issues = metadata['issues']
        for issue in issues:
            url = issue['url']
            parts = url.split('/')
            date = parts[-2]
            edition = parts[-1]
            # pull out the edition number
            ed = edition[3:-5]
            key = date + '-' + ed
            metadata_by_lccn[lccn].add(key)
            urls_by_key[lccn].append(url)

    for lccn, urls in urls_by_key.items():
        print(lccn, len(urls))
        random_url = np.random.choice(urls, size=1)[0]
        parts = random_url.split('/')
        fulldate = parts[-2]
        ed = parts[-1]
        outfile = os.path.join(seqs_dir, lccn + '_' + fulldate + '_' + ed)
        download(random_url, outfile)

    combined_lccns = sorted(set(articles_by_lccn).union(metadata_by_lccn))
    
    lccns = []
    article_count = []
    metadata_count = []
    missing_from_articles = []
    missing_from_metadata = []
    
    for i, lccn in enumerate(combined_lccns):
        lccns.append(lccn)
        article_count.append(len(articles_by_lccn[lccn]))
        metadata_count.append(len(metadata_by_lccn[lccn]))
        missing_from_articles.append(len(metadata_by_lccn[lccn] - articles_by_lccn[lccn]))
        missing_from_metadata.append(len(articles_by_lccn[lccn] - metadata_by_lccn[lccn]))
        
    df = pd.DataFrame()
    df['lccn'] = lccns
    df['article_count'] = article_count
    df['metadata_count'] = metadata_count
    df['missing_from_articles'] = missing_from_articles
    df['missing_from_metadata'] = missing_from_metadata
    
    outfile = os.path.join(basedir, 'edition_counts.csv')
    df.to_csv(outfile)


if __name__ == '__main__':
    main()
