import os
import time
import random
from optparse import OptionParser

from bs4 import BeautifulSoup

from common.requests_get import get


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)

    neurips_dir = os.path.join('data', 'neurips')
    if not os.path.exists(neurips_dir):
        os.makedirs(neurips_dir)

    base_url = 'https://papers.nips.cc'

    # get the list of conferences
    raw_html = get(base_url)
    html = BeautifulSoup(raw_html, 'html.parser')

    # get the links to each conference proceedings
    conference_urls = []
    hrefs = html.findAll('a')
    for href in hrefs:
        url = href.get('href')
        parts = url.split('/')
        if parts[1] == 'paper':
            conference_urls.append(url)

    print("Found {:d} conferences".format(len(conference_urls)))

    # for each conference get the links to all the papers
    for conf_url in conference_urls:
        paper_urls = []
        raw_html = get(base_url + conf_url)
        year = conf_url[-4:]
        year_dir = os.path.join(neurips_dir, year)
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)
        html = BeautifulSoup(raw_html, 'html.parser')
        hrefs = html.findAll('a')
        for href in hrefs:
            url = href.get('href')
            parts = url.split('/')
            if parts[1] == 'paper':
                paper_urls.append(url)
        print(year, len(paper_urls))

        # save them to a file for each year
        with open(os.path.join(year_dir, 'paper_urls.txt'), 'w') as f:
            for line in sorted(paper_urls):
                f.write(line + '\n')


if __name__ == '__main__':
    main()
