import os
import json
import time
import datetime as dt
from glob import glob
from optparse import OptionParser
from collections import Counter

import pandas as pd
#import wget

from common.requests_get import download


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--infile', type=str, default='/Users/dalc/data/LoC/books/sample/links.csv',
                      help='File with links: default=%default')
    parser.add_option('--outdir', type=str, default='/Users/dalc/data/LoC/books/sample/text/',
                      help='Output directory: default=%default')
    parser.add_option('--pause', type=int, default=2,
                      help='Pause between issues: default=%default')

    (options, args) = parser.parse_args()

    infile = options.infile
    outdir = options.outdir
    pause = options.pause

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    df = pd.read_csv(infile)

    filenames = df['Filename'].values
    urls = df['URL'].values

    for i, filename in enumerate(filenames):
        url = urls[i]
        outfile = os.path.join(outdir, filename)
        
        response = download(url, outfile, binary=True, stream=False, retry=True, ignore_content_type=True)

        if response is not None:
            print("Failed on", i, filename, url)        
            print(response)
        
        time.sleep(pause)

if __name__ == '__main__':
    main()
