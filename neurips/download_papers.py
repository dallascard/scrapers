import os
import re
import json
import glob
import time
import datetime as dt
from optparse import OptionParser
from collections import Counter

import wget
from bs4 import BeautifulSoup

from common.requests_get import get


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='data/neurips/',
                      help='Data directory: default=%default')
    parser.add_option('--first-year', type=int, default=1987,
                      help='First year: default=%default')
    parser.add_option('--last-year', type=int, default=2020,
                      help='Last year: default=%default')
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite files: default=%default')
    parser.add_option('--clear-log', action="store_true", default=False,
                      help='Clear log file before starting: default=%default')

    (options, args) = parser.parse_args()

    neurips_dir = options.basedir
    first = options.first_year
    last = options.last_year
    overwrite = options.overwrite
    clear_log = options.clear_log

    if not os.path.exists(neurips_dir):
        os.makedirs(neurips_dir)
    logfile = os.path.join(neurips_dir, 'errors.log')
    if clear_log:
        print("Clearing logfile:", logfile)
        with open(logfile, 'w') as f:
            f.write('')

    base_url = 'https://papers.nips.cc'

    link_name_counter = Counter()
    for year in range(first, last+1):
        n_pdfs = 0
        n_bibs = 0
        n_metadata = 0
        n_html = 0

        d = os.path.join(neurips_dir, str(year))
        print(d, year)

        html_dir = os.path.join(d, 'html')
        if not os.path.exists(html_dir):
            os.makedirs(html_dir)

        pdfs_dir = os.path.join(d, 'pdfs')
        if not os.path.exists(pdfs_dir):
            os.makedirs(pdfs_dir)

        metadata_dir = os.path.join(d, 'metadata')
        if not os.path.exists(metadata_dir):
            os.makedirs(metadata_dir)

        bib_dir = os.path.join(d, 'bibtex')
        if not os.path.exists(bib_dir):
            os.makedirs(bib_dir)

        paper_urls_file = os.path.join(d, 'paper_urls.txt')

        with open(paper_urls_file) as f:
            paper_urls = f.readlines()

        for paper_url in paper_urls:
            paper_url = paper_url.strip()
            raw_html = get(base_url + paper_url)
            if raw_html is None:
                print("Skipping", base_url + paper_url)
                with open(logfile, 'a') as f:
                    timestamp = str(dt.datetime.now())
                    f.write("{:s}: Failed on {:s}\n".format(timestamp, base_url + paper_url))
            else:
                html = BeautifulSoup(raw_html, 'html.parser')

                h4s = html.findAll('h4')
                meta = []
                for i, h4 in enumerate(h4s):
                    text = h4.text
                    if text == 'Authors':
                        assert i == 1
                        para = h4.find_next_sibling('p')
                        if para is not None:
                            text = para.text
                    elif text == 'Abstract':
                        assert i == 2
                        para = h4.find_next_sibling('p')
                        if para is not None:
                            text = para.text.strip()
                    meta.append(text)

                try:
                    assert len(meta) == 3
                except AssertionError as e:
                    print(paper_url)
                    raise e

                meta.append(base_url + paper_url)

                metadata = dict(zip(['title', 'authors', 'abstract', 'url'], meta))
                title = re.sub(r'\W+', '_', metadata['title'])
                assert len(title) > 0
                outfile = os.path.join(metadata_dir, title + '.json')
                if os.path.exists(outfile) and not overwrite:
                    pass
                else:
                    with open(outfile, 'w') as f:
                        json.dump(metadata, f, indent=2)
                        n_metadata += 1

                html_outfile = os.path.join(html_dir, title + '.html')
                if os.path.exists(html_outfile) and not overwrite:
                    pass
                else:
                    with open(html_outfile, 'wb') as f:
                        f.write(raw_html)
                        n_html += 1

                hrefs = html.findAll('a')
                for href in hrefs:
                    url = href.get('href')
                    text = href.text
                    if text.lower().startswith('paper'):
                        outfile = os.path.join(pdfs_dir, title + '.pdf')
                        success = download_file(base_url + url, outfile, max_tries=3, overwrite=overwrite)
                        if success:
                            n_pdfs += 1
                    if text.lower().startswith('bib'):
                        outfile = os.path.join(bib_dir, title + '.bib')
                        success = download_file(base_url + url, outfile, max_tries=3, overwrite=overwrite)
                        if success:
                            n_bibs += 1

        print("Downloaded: {:d} html, {:d} metadata, {:d} bibtex, {:d} pdfs of {:d} links".format(n_html, n_metadata, n_bibs, n_pdfs, len(paper_urls)))

        pdf_files = glob.glob(os.path.join(pdfs_dir, '*.pdf'))
        n_pdfs = len(pdf_files)

        files = glob.glob(os.path.join(bib_dir, '*.bib'))
        n_bibs = len(files)

        files = glob.glob(os.path.join(metadata_dir, '*.json'))
        n_metadata = len(files)

        files = glob.glob(os.path.join(html_dir, '*.html'))
        n_html = len(files)

        stats = {'html': n_html, 'metadata': n_metadata, 'bibtex': n_bibs, 'pdfs': n_pdfs, 'links': len(paper_urls)}
        print("Final numbers:")
        for k, v in stats.items():
            print(k, v)

        with open(os.path.join(d, 'stats.json'), 'w') as f:
            json.dump(stats, f, indent=2)

    for name, c in link_name_counter.most_common(n=20):
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
