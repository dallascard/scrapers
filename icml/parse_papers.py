import os
import re
import json
from glob import glob
from collections import Counter
from optparse import OptionParser

import spacy
from tqdm import tqdm

# Use Spacy to tokenize papers, trying to convert paragraphs of text into tokenized sentences, excluding references


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='data/icml/',
                      help='Data directory: default=%default')
    parser.add_option('--first-year', type=int, default=2008,
                      help='First year: default=%default')
    parser.add_option('--last-year', type=int, default=2020,
                      help='Last year: default=%default')
    parser.add_option('--min-sent-tokens', type=int, default=6,
                      help='Minimum length of sentence to keep (in tokens): default=%default')
    parser.add_option('--min-para-tokens', type=int, default=8,
                      help='Minimum length of paragraphs to keep (in tokens): default=%default')

    (options, args) = parser.parse_args()

    neurips_dir = options.basedir
    first = options.first_year
    last = options.last_year
    min_sent_tokens = options.min_sent_tokens
    min_para_tokens = options.min_para_tokens

    print("Loading spacy")
    nlp = spacy.load("en_core_web_sm")

    print("Parsing papers")
    outlines = []
    plain_sents = []
    count = 0
    n_files = 0
    n_papers = 0
    lines_counter = Counter()
    for year in range(first, last+1):
        print(year)
        text_files = sorted(glob(os.path.join(neurips_dir, str(year), 'text', '*.txt')))
        for infile in tqdm(text_files):
            n_files += 1
            basename = os.path.basename(infile)
            tokenized_sentences = tokenize(nlp, infile,min_para_tokens)
            if len(tokenized_sentences) == 0:
                print("\nError: No lines extracted from", infile)
            else:
                n_papers += 1
                lines_counter[len(tokenized_sentences)] += 1
            for sent in tokenized_sentences:
                # excluded short "sentences" and those that don't have any letters
                rejoined = ' '.join(sent)
                if len(sent) >= min_sent_tokens and re.match(r'.*[a-zA-Z].*', rejoined) is not None:
                    outline = {'id': 's' + str(count).zfill(7), 'year': year, 'paper': basename, 'tokens': [sent]}
                    outlines.append(outline)
                    plain_sents.append(rejoined)
                    count += 1

    print("Parsed {:d} sentences from {:d} papers / {:d} files".format(count, n_papers, n_files))
    print("min lines: {:d}".format(min(lines_counter)))
    print("max lines: {:d}".format(max(lines_counter)))
    outfile = os.path.join(neurips_dir, 'parsed.jsonlist')
    with open(outfile, 'w') as f:
        for line in outlines:
            f.write(json.dumps(line) + '\n')

    # also output plain text for perusing
    outfile = os.path.join(neurips_dir, 'parsed.txt')
    with open(outfile, 'w') as f:
        for line in plain_sents:
            f.write(line + '\n')


def tokenize(nlp, infile, min_para_tokens):

    with open(infile) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]

    # convert lines to paragraphs as best we can
    paragraphs = []
    new_paragraph = True
    #found_abstract_intro = False
    found_references = False
    for line in lines:
        # start collecting at the beginning, since not all papers mark the start of their abstract
        lower_line = line.lower()
        #if not found_references and 'abstract' in lower_line or 'introduction' in lower_line or 'background' in lower_line:
        #    found_abstract_intro = True
        # stop collecting when we see references or acknowledgements
        if 'references' in lower_line or 'acknowledgement' in lower_line or 'acknowledgment' in lower_line:
            found_references = True
        # try to take lines starting with the beginning and ending at the references
        if not found_references:
            # if a line is blank, start a new paragraph on the next line
            if len(line.strip()) == 0:
                new_paragraph = True
            # exclude lines that do not have any letters
            elif re.match(r'.*[a-zA-Z].*', line) is not None:
                if new_paragraph:
                    # start a new paragraph, and then continue it on the next line
                    paragraphs.append(line)
                    new_paragraph = False
                else:
                    # add this line on to the current paragraph
                    paragraphs[-1] += ' ' + line

    # parse each paragraph
    tokenized_sentences = []
    for paragraph in paragraphs:
        # exclude very short paragraphs
        if len(paragraph.split()) >= min_para_tokens:
            text = nlp(paragraph)
            for sent in text.sents:
                sent_tokens = [token.text for token in sent]
                tokenized_sentences.append(sent_tokens)

    return tokenized_sentences


if __name__ == '__main__':
    main()
