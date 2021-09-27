import os
import json
from optparse import OptionParser
from collections import defaultdict, Counter

import wget


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='data/iclr/',
                      help='Data directory: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    outdir = options.basedir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    base_url = 'https://www.loc.gov/cds/downloads/MDSConnect/'

    for part in range(1, 44):
        filename = 'BooksAll.2016.part' + str(part).zfill(2) + '.xml.gz'
        target_url = base_url + filename
        print(target_url)
        outfile = os.path.join(outdir, filename)
        wget.download(target_url, out=outfile)


if __name__ == '__main__':
    main()
