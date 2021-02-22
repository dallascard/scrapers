import os
import json
import hashlib
from glob import glob
from optparse import OptionParser
from collections import defaultdict, Counter


# Verify the checksums

def main():
    usage = "%prog index.json"
    parser = OptionParser(usage=usage)
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    index_file = args[0]

    parts = os.path.split(index_file)
    indir, filename = parts

    with open(index_file) as f:
        index = json.load(f)

    items = index['ocr']
    sha1s = {}
    for item in items:
        url = item['url']
        basedir, filename = os.path.split(url)
        sha1 = item['sha1']
        sha1s[filename] = sha1

    files = sorted(glob(os.path.join(indir, '*.tar.bz2')))
    for infile in files:
        sha1file = infile + '.sha1'
        with open(sha1file) as f:
            data = f.read()
        sha1 = data.split()[0]
        match = False
        basedir, filename = os.path.split(infile)
        if sha1 == sha1s[filename]:
            match = True
        print(match, infile, sha1, sha1s[infile])


if __name__ == '__main__':
    main()
