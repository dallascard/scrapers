import os
import re
from optparse import OptionParser

from common.requests_get import download, get
from bs4 import BeautifulSoup


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--save-dir', type=str, default='/Users/dalc/data/Exploring Music/',
                      help='Data directory: default=%default')

    (options, args) = parser.parse_args()

    save_dir = options.save_dir
    print(save_dir)

    links_file = os.path.join(save_dir, 'links.txt')
    with open(links_file) as f:
        urls = f.readlines()
    print(len(urls))

    for url in urls:
        print("Scraping", url)
        url = url.strip()
        raw = get(url)
        html = BeautifulSoup(raw, 'html.parser')

        # Get linked .mp3 files
        target = ''
        for script in html.findAll('script'):
            if script.text.strip().startswith('jQuery'):
                text = script.text.strip()
                target = text

        parts = target.split(',')

        file_links = []
        for p in parts:
            p = p.strip()
            if p.startswith('"file"'):
                link = re.sub('\\\\', '', p[8:-1])
                file_links.append(link)
            
        for link in file_links:
            basename = os.path.basename(link)
            outfile = os.path.join(save_dir, basename)
            print(basename)
            if not os.path.exists(outfile):
                download(link, outfile, binary=True, stream=True, retry=True, total=None, ignore_content_type=True)
            else:
                print("Already downloaded", outfile)

        print()



if __name__ == '__main__':
    main()
