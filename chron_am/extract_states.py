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

    metadata_dir = os.path.join(basedir, 'metadata')
    
    paper_places = {}
    paper_lccns = {}

    print("Reading metadata")
    files = sorted(glob(os.path.join(metadata_dir, '*.json')))
    for infile in tqdm(files):
        with open(infile) as f:
            metadata = json.load(f)
        lccn = metadata['lccn']
        title = metadata['name']
        place = metadata['place_of_publication']
        paper_places[title] = place
        paper_lccns[title] = lccn
    
    with open(os.path.join(basedir, 'paper_lccns.json'), 'w') as f:
        json.dump(paper_lccns, f)

    with open(os.path.join(basedir, 'paper_places.json'), 'w') as f:
        json.dump(paper_places, f)


if __name__ == '__main__':
    main()
