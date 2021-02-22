import os
import json
from glob import glob
from optparse import OptionParser
from collections import defaultdict, Counter


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
        parts = infile.split()
        filename = parts[1]
        outlines.append('tar -xvf ' + filename + ' --wildcards "*.txt"\n')

    with open(indir, 'untar_files.sh') as f:
        f.writelines(outlines)


if __name__ == '__main__':
    main()
