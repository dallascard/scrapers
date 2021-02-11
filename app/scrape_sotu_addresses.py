import os
import re
import json
import time
from optparse import OptionParser

from bs4 import BeautifulSoup
from common.urllib_get import urllib_get
from app.common import process_speech


def main():
    usage = "%prog\n" \
            "Scrape (spoken) state of the union addresses from the American Presidency Project"
    parser = OptionParser(usage=usage)
    parser.add_option('--outdir', type=str, default='data/app/sotu_addresses/',
                      help='Output directory): default=%default')
    parser.add_option('--pages', type=int, default=10,
                      help='Number of pages of results: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    pages = options.pages
    outdir = options.outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    raw_dir = os.path.join(outdir, 'raw')
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)

    domain = 'https://www.presidency.ucsb.edu'

    outlines = []
    for page in range(pages):
        if page == 0:
            url = 'https://www.presidency.ucsb.edu/documents/app-categories/spoken-addresses-and-remarks/presidential/state-the-union-addresses'
            index_file = os.path.join(outdir, 'index.html')
        else:
            url = 'https://www.presidency.ucsb.edu/documents/app-categories/spoken-addresses-and-remarks/presidential/state-the-union-addresses?page=' + str(page)
            index_file = os.path.join(outdir, 'index?page' + str(page) + '.html')

        if os.path.exists(index_file):
            print("Loading index page")
            with open(index_file, 'rb') as f:
                raw_html = f.read()
        else:
            print("Downloading index page")
            raw_html = urllib_get(url)
            time.sleep(2)
            print("Saving index page")
            with open(index_file, 'wb') as f:
                f.write(raw_html)

        html = BeautifulSoup(raw_html, 'html.parser')
        divs = html.findAll('div', {'class': ['field-title', 'col-sm-4']})

        link = None
        for d_i, div in enumerate(divs):
            links = div.findAll('a', href=True)
            if len(links) > 0:
                if d_i % 2 == 0:
                    link = links[0]['href']
                    print(d_i, link)
                else:
                    name = links[0].text.strip()
                    print(d_i, name)
                    assert link is not None
                    output = {'person': name, 'url': domain + link}
                    print("Scraping", domain + link)
                    output.update(process_speech(domain + link, raw_dir, verbose=False))
                    outlines.append(output)

    print("Saving {:d} addresses".format(len(outlines)))
    with open(os.path.join(outdir, 'sotu_addresses.all.jsonlist'), 'w') as fo:
        for line in outlines:
            fo.write(json.dumps(line) + '\n')


if __name__ == '__main__':
    main()
