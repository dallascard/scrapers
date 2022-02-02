import os
import json
import datetime as dt
from optparse import OptionParser
from collections import defaultdict, Counter

from tqdm import tqdm
from common.requests_get import download, get


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--outdir', type=str, default='data/chron_am/',
                      help='Output directory: default=%default')

    (options, args) = parser.parse_args()

    outdir = options.outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    target = 'https://chroniclingamerica.loc.gov/batches.json'
    outfile = os.path.join(outdir, 'index_00001.json')
    print(target, outfile)
    response = download(target, outfile)

    i = 2
    while response is not None:
        with open(outfile, 'r') as f:
            data = json.load(f)
        if 'next' not in data:
            response = None
        else:
            next_batch = data['next']
            outfile = os.path.join(outdir, 'index_{:s}.json'.format(str(i).zfill(5)))
            print(target, outfile)
            response = download(next_batch, outfile)
            i += 1


if __name__ == '__main__':
    main()
