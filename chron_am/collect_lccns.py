import os
import gzip
import json
import time
from glob import glob
from subprocess import run
from optparse import OptionParser
from collections import defaultdict, Counter

from tqdm import tqdm
from common.requests_get import download


# This script should download the metadata for each newspaper

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
    outfile = os.path.join(basedir, 'lccns.json')

    lccn_counter = Counter()

    files = sorted(glob(os.path.join(text_dir, '*.gz')))

    for infile in tqdm(files):
        with gzip.open(infile, 'rt') as f:
            lines = f.readlines()
        for line in lines:
            line = json.loads(line)
            lccn = line['sn']
            lccn_counter[lccn] += 1               
    print(len(lccn_counter), 'lccns')

    with open(outfile, 'w') as fo:
        json.dump(lccn_counter, fo)


if __name__ == '__main__':
    main()
