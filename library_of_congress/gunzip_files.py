import os
import json
from glob import glob
from subprocess import call
from optparse import OptionParser
from collections import defaultdict, Counter

# Download the public database of bibliographic metadata from the Library of Congress

def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='data/loc/',
                      help='Data directory: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    basedir = options.basedir
    files = sorted(glob(os.path.join(basedir, '*.gz')))

    for infile in files:
        cmd = ['gunzip', infile]
        print(' '.join(cmd))
        call(cmd)


if __name__ == '__main__':
    main()
