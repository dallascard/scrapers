import os
import re
import json
import time
from optparse import OptionParser

from bs4 import BeautifulSoup
from common.urllib_get import urllib_get


def main():
    usage = "%prog\n" \
            "Scrape State of the Union addresses from the web\n" \
            "Note: sometimes this will stall, but can be re-started at the same index using --start-link"
    parser = OptionParser(usage=usage)
    parser.add_option('--outdir', type=str, default='data/sotu/',
                      help='Output directory): default=%default')
    parser.add_option('--start-link', type=int, default=0,
                      help='First link index: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    outdir = options.outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    first_link = options.start_link

    domain = 'http://stateoftheunion.onetwothree.net/texts/'
    url = domain + 'index.html'
    raw_html = urllib_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')
    links = html.findAll('a', href=True)
    speeches = []
    for link_i, link in enumerate(links[first_link:]):
        href = link['href']
        parts = href.split('.')
        print(link_i + first_link, href)
        if len(parts) == 2 and len(parts[0]) == 8:
            try:
                date = int(parts[0])
                #print(len(speeches)+1, date)
                speech_url = domain + href
                raw_speech_html = urllib_get(speech_url)
                speech_html = BeautifulSoup(raw_speech_html, 'html.parser')
                headers = speech_html.findAll('h2')
                assert len(headers) == 1
                name = None
                for h in headers:
                    name = h.text
                paragraphs = []
                pblocks = speech_html.findAll('p')
                for p in pblocks:
                    text = p.text.strip()
                    # replace newlines
                    text = re.sub('\n', ' ', text)
                    if len(text) > 0:
                        paragraphs.append(text)

                output = {'name': name, 'date': date, 'text': paragraphs, 'url': href}

                with open(os.path.join(outdir, str(date) + '.jsonlist'), 'w') as fo:
                    json.dump(output, fo, indent=2, sort_keys=False)

                time.sleep(2)

            except TypeError:
                pass
            except Exception as e:
                print(e)
                raise e



if __name__ == '__main__':
    main()
