import os
import json
from optparse import OptionParser
from collections import defaultdict, Counter

from common.requests_get import download, get


# This script should download the index files for each batch of OCR files

def main():
    usage = "%prog basedir outdir"
    parser = OptionParser(usage=usage)
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    outdir = args[0]

    target = 1
    done = False
    while done is False:

        url = 'https://chroniclingamerica.loc.gov/batches/' + str(target) + '.json'
        outfile = os.path.join(outdir, str(target) + '.json')
        if not os.path.exists(outfile):
            download(url, outfile)

        with open(outfile) as f:
            data = json.load(f)

        next = data['next']
        if next is not None:
            filename = next.split('/')[-1]
            next_target = filename.split('.')[0]
            try:
                assert int(next_target) == target + 1
            except AssertionError as e:
                print(next)
                raise e
            target = next_target
        else:
            done = True


if __name__ == '__main__':
    main()
