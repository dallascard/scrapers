import os
import json
from optparse import OptionParser
from collections import defaultdict, Counter


# This script should download the .json metadata files for each paper downloaded and untarred using
# make_ocr_download_script.py and make_ocr_untar_script.py

def main():
    usage = "%prog basedir"
    parser = OptionParser(usage=usage)
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()


if __name__ == '__main__':
    main()
