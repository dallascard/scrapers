import os
import json
from glob import glob
from optparse import OptionParser
from collections import defaultdict, Counter

# Make a script to compute the sha1 checksums for downloaded .tar.bz2 files

def main():
    usage = "%prog basedir"
    parser = OptionParser(usage=usage)
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    indir = args[0]

    outlines = []

    files = sorted(glob(os.path.join(indir, '*.bz2')))
    for infile in files:
        parts = os.path.split(infile)
        filename = parts[1]
        outlines.append('sha1sum ' + filename + ' > ' + filename + '.sha1\n')

    with open(indir, 'compute_checksums.sh') as f:
        f.writelines(outlines)


if __name__ == '__main__':
    main()
