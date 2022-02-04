import os
import json
from optparse import OptionParser
from collections import defaultdict, Counter


def main():
    usage = "%prog download_script.sh"
    parser = OptionParser(usage=usage)
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    script = args[0]

    basedir = os.path.split(script)[0]
    print(basedir)

    with open(script) as f:
        lines = f.readlines()

    for line in lines:
        basename = line.split('/')[-1]
        filename = os.path.join(os.path.join(basedir, basename))
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(basename, file_size)
        else:
            print(basename, 'missing!')



if __name__ == '__main__':
    main()
