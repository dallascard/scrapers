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

    papers_by_lccn = defaultdict(set)

    print("Reading metadata")
    files = sorted(glob(os.path.join(metadata_dir, '*.json')))
    for infile in tqdm(files):
        with open(infile) as f:
            metadata = json.load(f)
        lccn = metadata['lccn']
        title = metadata['name']
        papers_by_lccn[lccn].add(title)

    # make sure there is at most one paper name per lccn
    for lccn, papers in papers_by_lccn.items():
        if len(papers) > 1:
            print(lccn, papers)

    # assuming the above is correct convert the sets to individual titles
    papers_by_lccn = {lccn: sorted(titles)[0] for lccn, titles in papers_by_lccn.items()}

    page_counts_by_year = defaultdict(Counter)
    word_counts_by_year = defaultdict(Counter)

    print("Reading articles")
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
            if lccn in papers_by_lccn:
                name = papers_by_lccn[lccn]
            else:
                name = lccn
            page_counts_by_year[name][year] += 1
            text = line['text']            
            tokens = text.split()
            word_counts_by_year[name][year] += len(tokens)

    outfile = os.path.join(basedir, 'page_counts_by_year.json')
    with open(outfile, 'w') as f:
        json.dump(page_counts_by_year, f)

    outfile = os.path.join(basedir, 'word_counts_by_year.json')
    with open(outfile, 'w') as f:
        json.dump(word_counts_by_year, f)


if __name__ == '__main__':
    main()
