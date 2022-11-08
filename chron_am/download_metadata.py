import os
import gzip
import json
import time
import shutil
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
    
    metadata_dir = os.path.join(basedir, 'metadata')    
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)

    lccn_file = os.path.join(basedir, 'lccns.json')
    with open(lccn_file, 'r') as f:
        lccn_counter = Counter(json.load(f))

    for lccn_i, lccn in enumerate(lccn_counter):
        count = lccn_counter[lccn]
        print(lccn, count, '({:d}/{:d})'.format(lccn_i, len(lccn_counter)))
        url = 'https://chroniclingamerica.loc.gov/lccn/' + str(lccn) + '.json'
        filename = lccn + '.json'
        outfile = os.path.join(metadata_dir, filename)

        attempts = 0
        
        if overwrite and os.path.exists(outfile):
            shutil.rmtree(outfile)
        
        while not os.path.exists(outfile):
            download(url, outfile)
            #command = ['wget', url, '-P', outfile]
            #print("Downloading from", url, "(attempt {:d}".format(attempts))
            #print(' '.join(command))
            #run(command)            
            
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
