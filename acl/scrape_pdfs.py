import os
import time
import random
from subprocess import call
from optparse import OptionParser

from bs4 import BeautifulSoup

from common.requests_get import download


# Currently a dedicated script for EMNLP 2019, but could be changed


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--conf', type=str, default='emnlp',
                      help='Conference: default=%default')
    parser.add_option('--year', type=str, default='2019',
                      help='Year: default=%default')
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite files to download: default=%default')


    (options, args) = parser.parse_args()

    conf = options.conf
    year = options.year
    overwrite = options.overwrite

    conf_dir = os.path.join('data', 'acl', conf, str(year))
    output_dir = os.path.join(conf_dir, 'pdfs')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    url = 'https://www.aclweb.org/anthology/events/' + conf + '-' + year + '/index.html'
    outfile = os.path.join(conf_dir, 'index.html')

    if os.path.exists(outfile) and overwrite:
        print("Deleting existing index file")
        os.remove(outfile)
        
    if not os.path.exists(outfile):
        print("Downloading index")
        cmd = ['wget', url, '-P', conf_dir]
        print(' '.join(cmd))
        call(cmd)

    print("Reading index")
    with open(outfile, 'rb') as f:        
        raw_html = f.read()

    html = BeautifulSoup(raw_html, 'html.parser')

    pdf_urls = set()
    hrefs = html.findAll('a', {'title': "Open PDF"})
    for href in hrefs:
        url = href.get('href')
        parts = url.split('/')
        name = parts[-1]
        parts = name.split('.')
        if len(parts) == 2:
            if len(parts[0]) == 8 and parts[1] == 'pdf':
                pdf_urls.add(url)

    pdf_urls = list(pdf_urls)
    pdf_urls.sort()

    max_tries = 3

    n_urls = len(pdf_urls)
    
    print()
    print(n_urls, 'pdfs found')
    print()

    for url_i, url in enumerate(pdf_urls):
        tries = 0
        success = False
        parts = url.split('/')
        name = parts[-1]
        outfile = os.path.join(output_dir, name)
        if os.path.exists(outfile) and overwrite:
            print("Deleting old pdf")
            os.remove(outfile)
        if os.path.exists(outfile):
            print("({:d}/{:d}) Skipping {:s}".format(url_i, n_urls, url))
        else:
            while tries < max_tries and not success:
                #try:
                print("({:d}/{:d}) Downloading {:s}".format(url_i, n_urls, url))
                cmd = ['wget', url, '-P', output_dir]
                print(' '.join(cmd))
                call(cmd)

                if os.path.exists(outfile):
                    success = True
                    print()
                    time.sleep(1)
                else:

                #except Exception as e:
                    print("Download failed on", url)
                    if os.path.exists(outfile):
                        os.remove(outfile)
                    if tries < max_tries:
                        print("Pausing for 3 seconds...")
                        time.sleep(3)
                        tries += 1
                    else:                        
                        raise RuntimeError("Maximum number of tries exceeded on", url)


if __name__ == '__main__':
    main()
