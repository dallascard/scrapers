import os
import json
from optparse import OptionParser
from collections import defaultdict, Counter

from common.requests_get import download


# This script should download the index files for each batch of OCR files

def main():
    usage = "%prog basedir"
    parser = OptionParser(usage=usage)
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    basedir = args[0]

    group_dir = os.path.join(basedir, 'grouped_batches')
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)

    batch_dir = os.path.join(basedir, 'batches')
    if not os.path.exists(batch_dir):
        os.makedirs(batch_dir)

    lccn_dir = os.path.join(basedir, 'lccns')
    if not os.path.exists(lccn_dir):
        os.makedirs(lccn_dir)

    lccn_counter = Counter()

    target = 1
    done = False
    while done is False:
        print(target)
        # Download this target index file
        url = 'https://chroniclingamerica.loc.gov/batches/' + str(target) + '.json'
        outfile = os.path.join(group_dir, str(target) + '.json')
        if not os.path.exists(outfile):
            download(url, outfile)

        # open it up
        with open(outfile) as f:
            data = json.load(f)

        # download the metadata for each batch
        for batch in data['batches']:
            url = batch['url']
            filename = url.split('/')[-1]
            outfile = os.path.join(batch_dir, filename)
            if not os.path.exists(outfile):
                download(url, outfile)

            # download the metadata associated with each lccn
            with open(outfile) as f:
                batch_metadata = json.load(f)

            lccns = batch_metadata['lccns']
            for lccn in lccns:
                lccn_counter[lccn] += 1
                url = 'https://chroniclingamerica.loc.gov/lccn/' + str(lccn) + '.json'
                outfile = os.path.join(lccn_dir, filename)
                if os.path.exists(outfile):
                    print("Skipping existing lccn:", lccn)
                else:
                    download(url, outfile)

        # get the next group of batches
        if 'next' in data['next'] and data['next'] is not None:
            next_link = data['next']
            print(next_link)
            filename = next_link.split('/')[-1]
            next_target = filename.split('.')[0]
            assert int(next_target) == target + 1
            target = int(next_target)
        else:
            done = True

    for lccn, count in lccn_counter.most_common(n=10):
        print(lccn, count)


if __name__ == '__main__':
    main()
