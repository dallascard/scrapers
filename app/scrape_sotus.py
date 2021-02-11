import os
import json
from optparse import OptionParser

from bs4 import BeautifulSoup
from common.urllib_get import urllib_get
from app.common import process_speech


# Scrape the state of the union speeches from the American Presidency Project
# Note that this script uses an older interface which tries to get all relevant SOTU speeches
# Separate scripts exist for the new interface to get SOTU addresses and messages separately

def main():
    usage = "%prog\n" \
            "Scrape State of the Union addresses from the American Presidency Project"
    parser = OptionParser(usage=usage)
    parser.add_option('--outdir', type=str, default='data/app/sotu/',
                      help='Output directory): default=%default')
    #parser.add_option('--start-link', type=int, default=0,
    #                  help='First link index: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    outdir = options.outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    raw_dir = os.path.join(outdir, 'raw')
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)

    #parsed_dir = os.path.join(outdir, 'parsed')
    #if not os.path.exists(parsed_dir):
    #    os.makedirs(parsed_dir)

    index_file = os.path.join(outdir, 'index.html')

    if os.path.exists(index_file):
        print("Loading index page")
        with open(index_file, 'rb') as f:
            raw_html = f.read()
    else:
        print("Downloading index page")
        url = 'https://www.presidency.ucsb.edu/documents/presidential-documents-archive-guidebook/annual-messages-congress-the-state-the-union'
        raw_html = urllib_get(url)
        print("Saving index page")
        with open(index_file, 'wb') as f:
            f.write(raw_html)

    html = BeautifulSoup(raw_html, 'html.parser')
    tables = html.findAll('tbody')

    outlines = []
    for table in tables[:1]:
        name = None
        table_rows = table.findAll('tr')
        for r_i, row in enumerate(table_rows[1:]):
            term = None
            cells = row.findAll('td')
            print(r_i, len(cells))
            # skip a problem with bad HTML that wraps rows in another row
            if len(cells) > 12:
                pass
            elif len(cells) > 2:
                # we're in the upper part of the table, so look at all cells
                for c_i, cell in enumerate(cells):

                    if c_i == 0:
                        cell_text = cell.text.strip()
                        if cell_text != '':
                            name = cell_text
                        print(name)
                    elif c_i == 1:
                        term = cell.text.strip()
                        print(term)
                    else:
                        links = cell.findAll('a', href=True)
                        if len(links) > 0:
                            if c_i > 6:
                                written = True
                            else:
                                written = False
                            year = cell.text.strip()
                            # treat Nixon's 1973 separately
                            print(r_i, c_i, cell.text)
                            if year != '1973†':
                                if len(year) > 4 and year[4] == '*':
                                    sotu = False
                                else:
                                    sotu = True

                                link = links[0]['href']

                                output = {'person': name,
                                          'term': term,
                                          'year': int(year[:4]),
                                          'is_sotu': sotu,
                                          'written': written,
                                          'url': link}

                                output.update(process_speech(link, raw_dir))

                                outlines.append(output)

                        else:
                            print(c_i, cell.text)

            elif len(cells) == 2:
                # we're in the upper part of the table (for Nixon's 1973 speeches)
                for c_i, cell in enumerate(cells):
                    # first check to see if we're in the end of the table, with Nixon's 1973 messages
                    if c_i == 1:
                        links = cell.findAll('a', href=True)
                        if len(links) > 0:
                            link = links[0]['href']
                            print(r_i, c_i, cell.text, link)
                            output = {'person': 'Richard M. Nixon',
                                      'term': '1973-1974',
                                      'year': 1973,
                                      'is_sotu': True,
                                      'written': True}
                            output.update(process_speech(link, raw_dir))
                            outlines.append(output)
            else:
                print(r_i, cells[0].text)

    print("Saving {:d} speeches".format(len(outlines)))
    with open(os.path.join(outdir, 'sotu.all.jsonlist'), 'w') as fo:
        for line in outlines:
            fo.write(json.dumps(line) + '\n')


if __name__ == '__main__':
    main()
