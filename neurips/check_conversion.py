import os
import glob
from optparse import OptionParser


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='data/neurips/',
                      help='Data directory: default=%default')

    (options, args) = parser.parse_args()

    neurips_dir = options.basedir

    year_dirs = sorted(glob.glob(os.path.join(neurips_dir, '*')))
    for year_dir in year_dirs:
        pdf_dir = os.path.join(year_dir, 'pdfs')
        text_dir = os.path.join(year_dir, 'text')

        pdfs = glob.glob(os.path.join(pdf_dir, '*.pdf'))
        texts = glob.glob(os.path.join(text_dir, '*.txt'))

        print(year_dir, len(pdfs), len(texts), len(pdfs) - len(texts))


if __name__ == '__main__':
    main()
