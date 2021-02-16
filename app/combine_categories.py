import os
import json
from glob import glob
from optparse import OptionParser
from collections import defaultdict, Counter


def main():
    usage = "%prog scrapers_dir"
    parser = OptionParser(usage=usage)
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    scrapers_dir = args[0]

    files = sorted(glob(os.path.join(scrapers_dir, 'data', 'app', '*', 'all.jsonlist')))

    url_counter = Counter()
    outlines = []
    for infile in files:
        parts = infile.split('/')
        category = parts[-2]
        with open(infile) as f:
            lines = f.readlines()
        lines = [json.loads(line) for line in lines]
        for line in lines:
            line['category'] = category
            url_counter[line['url']] += 1
        outlines.extend(lines)

    print(len(outlines), len(url_counter))


if __name__ == '__main__':
    main()
