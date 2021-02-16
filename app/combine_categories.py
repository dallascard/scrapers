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
    outlines = defaultdict(list)
    for infile in files:
        parts = infile.split('/')
        category = parts[-2]
        print(category)
        with open(infile) as f:
            lines = f.readlines()
        lines = [json.loads(line) for line in lines]
        for line in lines:
            line['category'] = category
            url = line['url']
            outlines[url].append(line)

    category_groups = Counter()
    length_counter = Counter()
    for url, lines in outlines.items():
        length_counter[len(lines)] += 1
        if len(lines) == 2:
            try:
                assert lines[0]['title'] == lines[1]['title']
                assert lines[0]['date'] == lines[1]['date']
                for p_i, para in lines[0]['text']:
                    assert lines[0]['text'][p_i] == lines[1]['text'][p_i]

            except AssertionError as e:
                print(lines[0])
                print(lines[1])
                raise e
            #assert lines[0]['text'] == lines[1]['test']

        if len(lines) > 1:
            categories = tuple(sorted([line['category'] for line in lines]))
            category_groups[categories] += 1

    for length, count in length_counter.most_common():
        print(length, count)

    for group, count in category_groups.most_common():
        print(group, count)


if __name__ == '__main__':
    main()
