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
    parser.add_option('--basedir', type=str, default='data/icml/',
                      help='Data directory: default=%default')
    parser.add_option('--first-year', type=int, default=2009,
                      help='First year: default=%default')
    parser.add_option('--last-year', type=int, default=2020,
                      help='Last year: default=%default')
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite files: default=%default')
    parser.add_option('--clear-log', action="store_true", default=False,
                      help='Clear log file before starting: default=%default')

    (options, args) = parser.parse_args()

    icml_dir = options.basedir
    first = options.first_year
    last = options.last_year
    overwrite = options.overwrite
    clear_log = options.clear_log

    if not os.path.exists(icml_dir):
        os.makedirs(icml_dir)

    logfile = os.path.join(icml_dir, 'errors.log')
    if clear_log:
        print("Clearing logfile:", logfile)
        with open(logfile, 'w') as f:
            f.write('')

    link_name_counter = Counter()
    for year in range(first, last+1):
        year_dir = os.path.join(icml_dir, str(year))
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)

        outdir = os.path.join(icml_dir, str(year), 'pdfs')
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        supp_dir = os.path.join(icml_dir, str(year), 'supp_pdfs')
        if not os.path.exists(supp_dir):
            os.makedirs(supp_dir)

        print(outdir)

        infile = os.path.join('icml', 'links', str(year), str(year) + '.txt')
        n_links = 0
        n_supp_links = 0
        n_pdfs = 0
        n_supp_pdfs = 0
        with open(infile) as f:
            lines = f.readlines()

        for line in lines:
            if line.strip()[-4:] == '.pdf':
                paper_url = line.strip()
                filename = os.path.basename(paper_url)
                link_name_counter[paper_url] += 1
                if '-supp' in line:
                    outfile = os.path.join(supp_dir, filename)
                    n_supp_links += 1
                else:
                    outfile = os.path.join(outdir, filename)
                    n_links += 1
                success = download_file(paper_url, outfile, max_tries=3, overwrite=overwrite)
                if success:
                    if '-supp' in line:
                        n_supp_pdfs += 1
                    else:
                        n_pdfs += 1

        print("Downloaded: {:d} pdfs of {:d} links".format(n_pdfs, n_links))
        print("Downloaded: {:d} pdfs of {:d} supplementary links".format(n_supp_pdfs, n_supp_links))

        stats = {'pdfs': n_pdfs, 'supp_pdfs': n_supp_pdfs}
        print("Final numbers:")
        for k, v in stats.items():
            print(k, v)

        with open(os.path.join(year_dir, 'stats.json'), 'w') as f:
            json.dump(stats, f, indent=2)

    # check for duplicate link names
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
