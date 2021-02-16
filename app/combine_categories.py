import os
import json
from glob import glob
from optparse import OptionParser
from collections import defaultdict, Counter


def main():
    usage = "%prog scrapers_dir outfile.jsonlist"
    parser = OptionParser(usage=usage)
    #parser.add_option('--issue', type=str, default='immigration',
    #                  help='Issue: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    scrapers_dir = args[0]
    outfile = args[1]

    files = sorted(glob(os.path.join(scrapers_dir, 'data', 'app', '*', 'all.jsonlist')))

    documents = defaultdict(list)
    for infile in files:
        parts = infile.split('/')
        category = parts[-2]
        print(category)
        with open(infile) as f:
            lines = f.readlines()
        lines = [json.loads(line) for line in lines]
        for line in lines:
            url = line['url']
            if url in documents:
                assert documents[url]['title'] == line['title']
                assert documents[url]['date'] == line['date']
                assert documents[url]['person'] == line['person']
                for p_i, para in enumerate(line['text']):
                    assert para == documents[url]['text'][p_i]
                documents[url]['categories'].add(category)
            else:
                line['categories'] = {category}
                documents[url] = line

    category_counter = Counter()
    category_group_counter = Counter()
    print(len(documents))
    with open(outfile, 'w') as f:
        for url, line in documents.items():
            # convert set to list for serialization
            categories = sorted(line['categories'])
            category_counter.update(categories)
            category_group_counter[tuple(categories)] += 1
            line['categories'] = categories
            f.write(json.dumps(line) + '\n')

    for category, count in category_counter.most_common():
        print(category, count)

    for group, count in category_group_counter.most_common():
        print(group, count)

if __name__ == '__main__':
    main()
