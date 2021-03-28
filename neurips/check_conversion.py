import os
import glob
from optparse import OptionParser


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    #parser.add_option('--year', type=str, default='*',
    #                  help='Year to process ("*" for all): default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    neurips_dir = os.path.join('data', 'neurips')
    year_dirs = sorted(glob.glob(os.path.join(neurips_dir, '*')))
    for year_dir in year_dirs:
        pdf_dir = os.path.join(year_dir, 'pdfs')
        text_dir = os.path.join(year_dir, 'text')

        pdfs = glob.glob(os.path.join(pdf_dir, '*.pdf'))
        texts = glob.glob(os.path.join(text_dir, '*.txt'))

        print(year_dir, len(pdfs), len(texts), len(pdfs) - len(texts))


if __name__ == '__main__':
    main()
