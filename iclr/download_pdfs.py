import os
import json
import time
from glob import glob
from optparse import OptionParser
from collections import Counter

import wget


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='data/iclr/',
                      help='Data directory: default=%default')
    parser.add_option('--first-year', type=int, default=2018,
                      help='First year: default=%default')
    parser.add_option('--last-year', type=int, default=2021,
                      help='Last year: default=%default')
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite files: default=%default')
    parser.add_option('--clear-log', action="store_true", default=False,
                      help='Clear log file before starting: default=%default')

    (options, args) = parser.parse_args()

    iclr_dir = options.basedir
    first = options.first_year
    last = options.last_year
    overwrite = options.overwrite
    clear_log = options.clear_log

    if not os.path.exists(iclr_dir):
        os.makedirs(iclr_dir)

    logfile = os.path.join(iclr_dir, 'errors.log')
    if clear_log:
        print("Clearing logfile:", logfile)
        with open(logfile, 'w') as f:
            f.write('')

    link_name_counter = Counter()
    for year in range(first, last+1):

        year_dir = os.path.join(iclr_dir, str(year))
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)

        files = sorted(glob(os.path.join('iclr', 'links', str(year), 'conference', '*.txt')))
        for infile in files:
            n_pdfs = 0
            n_links = 0
            basename = os.path.basename(infile)
            paper_type = basename.split('.')[1]
            with open(infile) as f:
                lines = f.readlines()

            paper_type_dir = os.path.join(iclr_dir, str(year), 'conference', paper_type)
            outdir = os.path.join(iclr_dir, str(year), 'conference', paper_type, 'pdfs')
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            print(outdir)

            for line in lines:
                if line.startswith('https://openreview.net/pdf?'):
                    n_links += 1
                    paper_url = line.strip()
                    paper_id = paper_url.split('=')[-1]
                    link_name_counter[paper_url] += 1
                    outfile = os.path.join(outdir, paper_id + '.pdf')
                    success = download_file(paper_url, outfile, max_tries=3, overwrite=overwrite)
                    if success:
                        n_pdfs += 1

            print("Downloaded: {:d} pdfs of {:d} links".format(n_pdfs, n_links))

            stats = {'pdfs': n_pdfs}
            print("Final numbers:")
            for k, v in stats.items():
                print(k, v)

            with open(os.path.join(paper_type_dir, 'stats.json'), 'w') as f:
                json.dump(stats, f, indent=2)

    for name, c in link_name_counter.most_common(n=5):
        print(name, c)


def download_file(url, outfile, max_tries=3, logfile=None, overwrite=False):
    tries = 0
    success = False
    if os.path.exists(outfile) and not overwrite:
        print("Skipping {:s}".format(url))
    else:
        if os.path.exists(outfile) and overwrite:
            print("Deleting", outfile)
            os.remove(outfile)
        while tries < max_tries and not success:
            try:
                print("Downloading {:s}".format(url))
                wget.download(url, out=outfile)
                success = True
            except Exception as e:
                print("Download failed on", url)
                if os.path.exists(outfile):
                    os.remove(outfile)
                if tries < max_tries:
                    print("Pausing for 3 seconds...")
                    time.sleep(3)
                    tries += 1
                else:
                    print("Maximum number of tries exceeded on", url)
                    if logfile is not None:
                        with open(logfile, 'a') as f:
                            f.write("Maximum number of tries exceeded on" + url + '\n')
                    raise e
    print()
    return success


if __name__ == '__main__':
    main()
