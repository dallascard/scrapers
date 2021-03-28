import os
import glob
import json
import subprocess
from optparse import OptionParser

def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--first-year', type=int, default=1987,
                      help='First year: default=%default')
    parser.add_option('--last-year', type=int, default=2020,
                      help='Last year: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    first = options.first_year
    last = options.last_year

    neurips_dir = os.path.join('data', 'neurips')

    for year in range(first, last+1):
        year_dirs = glob.glob(os.path.join(neurips_dir, str(year)))
        for year_dir in year_dirs:
            pdf_dir = os.path.join(year_dir, 'pdfs')
            text_dir = os.path.join(year_dir, 'text')
            if not os.path.exists(text_dir):
                os.makedirs(text_dir)

            files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
            files.sort()
            for infile in files:
                basename = os.path.basename(infile)
                name = os.path.splitext(basename)[0]
                cmd = ['pdftotext', infile, os.path.join(text_dir, name + '.txt')]
                print(' '.join(cmd))
                subprocess.call(cmd)

            files = glob.glob(os.path.join(text_dir, '*.txt'))
            n_text = len(files)

            print("Converted {:d} files".format(n_text))

            stats_file = os.path.join(year_dir, 'stats.json')
            with open(stats_file) as f:
                stats = json.load(f)

            stats['text'] = n_text
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)


if __name__ == '__main__':
    main()
