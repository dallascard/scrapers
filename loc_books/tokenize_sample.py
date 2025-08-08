import os
import re
import json
import time
import datetime as dt
from glob import glob
from optparse import OptionParser
from collections import Counter

import spacy


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--indir', type=str, default='/Users/dalc/data/LoC/books/sample/text/',
                      help='Output directory: default=%default')
    parser.add_option('--outdir', type=str, default='/Users/dalc/data/LoC/books/sample/tokenized/',
                      help='Output directory: default=%default')

    (options, args) = parser.parse_args()

    indir = options.indir
    outdir = options.outdir

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    files = sorted(glob(os.path.join(indir, '*.txt')))
    nlp = spacy.load('en_core_web_sm')

    nlp.max_length = 1500000
    
    for infile in files:
        print(infile)
        with open(infile, 'r') as f:
            lines = f.readlines()

        text = ''
        for line_i, line in enumerate(lines[:-1]):
            if lines[line_i+1] == '\n':
                text += line.strip() + '\n'
            else:
                text += line.strip() + ' '
        text += lines[-1].strip()

        text = re.sub('\n+', '\n\n', text)

        outfile = os.path.join(outdir, os.path.basename(infile))
        with open(outfile, 'w') as f:
            f.write(text)

        try:
            doc = nlp(text, disable=['parser', 'ner'])

            tokens = []
            for token in doc:
                tokens.append(token.text)

            doc = {'tokens': tokens}

            outfile = os.path.join(outdir, os.path.basename(infile))[:-3] + 'json'
            with open(outfile, 'w') as f:
                json.dump(doc, f)
        except ValueError as e:
            print(e)        



if __name__ == '__main__':
    main()
