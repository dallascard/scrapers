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
    parser.add_option('--download-mp3s', action="store_true", default=False,
                      help='Download mp3 files: default=%default')

    (options, args) = parser.parse_args()

    save_dir = options.save_dir
    download_mp3s = options.download_mp3s

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    url = 'https://www.wfmt.com/programs/exploring-music/'
    raw = get(url)

    html = BeautifulSoup(raw, 'html.parser')

    # get links to other episodes
    links = []
    for link in html.findAll('a'):
        href = link.get('href')
        if href is not None:
            if href.startswith('https://'):
                print(href)
                parts = href.split('/')
                if len(parts) > 6:
                    if len(parts[3]) == 4 and len(parts[4]) == 2 and len(parts[5]) == 2:
                        links.append(href)
    
    with open(os.path.join(save_dir, 'links.txt'), 'w') as f:
        for link in links:
            f.write(link + '\n')

    if download_mp3s:
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




if __name__ == '__main__':
    main()
