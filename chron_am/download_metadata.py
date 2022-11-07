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
    parser.add_option('--pause', type=int, default=10,
                      help='Time to wait on error: default=%default')
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite tar files: default=%default')
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    basedir = options.basedir
    pause = options.pause
    overwrite = options.overwrite

    text_dir = os.path.join(basedir, 'text_only')
    metadata_dir = os.path.join(basedir, 'metadata')    
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)

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

    for lccn, count in lccn_counter.most_common():
        print(lccn, count)
        url = 'https://chroniclingamerica.loc.gov/lccn/' + str(lccn) + '.json'
        filename = lccn + '.json'
        outfile = os.path.join(metadata_dir, filename)
        download(url, outfile)

        attempts = 0
        
        if overwrite and os.path.exists(outfile):
            os.remove(outfile)
        
        while not os.path.exists(outfile):
            command = ['wget', url, '-P', outfile]
            print("Downloading from", url, "(attempt {:d}".format(attempts))
            print(' '.join(command))
            run(command)            
            
            if not os.path.exists(outfile):
                print("** ERROR **: File not downloaded:", outfile)
                print("Sleeping for 180 seconds")
                time.sleep(180)

            elif os.path.getsize(outfile) == 0:
                raise RuntimeError("** ERROR **: Empty file:", outfile)
            
            attempts += 1

            if attempts >= 10:
                raise RuntimeError("Failed 10 times on", url)
    
        print("Pausing for {:d} seconds".format(pause))
        time.sleep(pause)

if __name__ == '__main__':
    main()
