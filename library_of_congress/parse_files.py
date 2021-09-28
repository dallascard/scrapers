import os
import json
from glob import glob
from optparse import OptionParser
from collections import defaultdict, Counter

from lxml import etree

# Parse the xml files from LoC

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

    author_counter = Counter()

    for infile in files[:1]:
        print("Reading", infile)
        parser = etree.XMLParser(attribute_defaults=True, dtd_validation=True, huge_tree=True)
        tree = etree.parse(infile, parser)

        for elem in tree.iter():
            records = elem
            break

        entries = records.getchildren()

        count = 0
        print("Parsing author pages")
        for entry in entries:
            if entry.tag == 'record':
                for child in entry.getchildren():
                    if child.tag == 'datafield':
                        tag = child.attrib['tag']
                        if tag == '100':
                            for subchild in child.getchildren():
                                if subchild.tag == 'subfield':
                                    code = subchild.attrib['code']
                                    if code == 'a':
                                        author = subchild.text
                                        author_counter[author] += 1

    for a, c in author_counter.most_common(n=20):
        print(a, c)


if __name__ == '__main__':
    main()
