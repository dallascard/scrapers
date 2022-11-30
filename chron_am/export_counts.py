import os
import gzip
import json
import datetime
from glob import glob
from subprocess import run
from optparse import OptionParser
from collections import defaultdict, Counter

import numpy as np
import pandas as pd
from tqdm import tqdm

from common.requests_get import download


# Count the number of articles and words for each paper over time

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
    
    files = sorted(glob(os.path.join(text_dir, '*.gz')))

    seq_count_by_date = defaultdict(Counter)
    word_count_by_date = defaultdict(Counter)

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
            #key = str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + '-' + str(ed)
            #date = datetime.date(year, month, day)
            date = str(year).zfill(4) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2)
            seq_count_by_date[lccn][date] += 1
            text = line['text']            
            tokens = text.split()
            word_count_by_date[lccn][date] += len(tokens)

    papers_by_lccn = defaultdict(set)

    print("Reading metadata")
    files = sorted(glob(os.path.join(metadata_dir, '*.json')))
    for infile in tqdm(files):
        with open(infile) as f:
            metadata = json.load(f)
        lccn = metadata['lccn']
        title = metadata['name']
        papers_by_lccn[lccn].add(title)

    for lccn, papers in papers_by_lccn.items():
        if len(papers) > 1:
            print(lccn, papers)

    outfile = os.path.join(basedir, 'article_counts_by_date.json')
    with open(outfile, 'w') as f:
        json.dump(seq_count_by_date, f)


if __name__ == '__main__':
    main()
