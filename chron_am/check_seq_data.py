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
    #metadata_dir = os.path.join(basedir, 'metadata')
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

    lccns = []
    fulldates = []
    eds = []
    text_counts = []
    metadata_counts = []

    seq_files = sorted(glob(os.path.join(seqs_dir, '*.json')))
    for infile in seq_files:        
        with open(infile) as f:
            seq_data = json.load(f)
        basename = os.path.basename(infile)
        parts = basename.split('_')
        lccn = parts[0]
        fulldate = parts[1]
        ed = parts[2][3:-5]
        key = fulldate + '-' + str(ed)
        n_pages = len(seq_data['pages'])
        lccns.append(lccn)
        fulldates.append(fulldate)
        eds.append(ed)
        text_counts.append(seq_counts[lccn][key])
        metadata_counts.append(n_pages)

    df = pd.DataFrame()
    df['lccn'] = lccns
    df['date'] = fulldates
    df['ed'] = eds
    df['article_counts'] = text_counts
    df['metadata_counts'] = metadata_counts
    df['diff'] = df['article_counts'] - df['metadata_counts']
    
    outfile = os.path.join(basedir, 'seq_counts.csv')
    df.to_csv(outfile)


if __name__ == '__main__':
    main()
