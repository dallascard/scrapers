import os
import json
from optparse import OptionParser
from collections import defaultdict, Counter

from common.requests_get import download, get


# This script should download the index files for each batch of OCR files

def main():
    usage = "%prog basedir"
    parser = OptionParser(usage=usage)
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    basedir = args[0]

    group_dir = os.path.join(basedir, 'grouped_batches')
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)

    outdir = os.path.join(basedir, 'batches')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    target = 1
    done = False
    while done is False:
        print(target)
        # Download this target index file
        url = 'https://chroniclingamerica.loc.gov/batches/' + str(target) + '.json'
        outfile = os.path.join(group_dir, str(target) + '.json')
        if not os.path.exists(outfile):
            download(url, outfile)

        # open it up
        with open(outfile) as f:
            data = json.load(f)

        # download the metadata for each batch
        for batch in data['batches']:
            url = batch['url']
            filename = url.split('/')[-1]
            outfile = os.path.join(outdir, filename)
            if not os.path.exists(outfile):
                download(url, outfile)

        next = data['next']
        if next is not None:
            print(next)
            filename = next.split('/')[-1]
            next_target = filename.split('.')[0]
            assert int(next_target) == target + 1
            target = int(next_target)
        else:
            done = True



if __name__ == '__main__':
    main()
