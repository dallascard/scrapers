import os
import json
from optparse import OptionParser
from collections import defaultdict, Counter

from tqdm import tqdm

def main():
    usage = "%prog infile.jsonlist outfile.jsonlist"
    parser = OptionParser(usage=usage)
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    infile = args[0]
    outfile = args[1]

    with open(infile) as f:
        lines = f.readlines()
    print("Loaded {:d} documents".format(len(lines)))

    outlines = []
    for line in tqdm(lines):
        line = json.loads(line)
        url = line['url']
        paragraphs = line['text']
        for p_i, p in enumerate(paragraphs):
            outlines.append({'id': url + '_' + str(p_i).zfill(4), 'text': p})

    print("Saving {:d} lines".format(len(outlines)))
    with open(outfile, 'w') as f:
        for line in outlines:
            f.write(json.dumps(line) + '\n')


if __name__ == '__main__':
    main()
