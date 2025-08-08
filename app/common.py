import os
import json
import time

from bs4 import BeautifulSoup
from common.urllib_get import urllib_get


def scrape_documents(initial_target, outdir, overwrite_index_pages=False, overwrite_all=False, sleep=2, domain='https://www.presidency.ucsb.edu'):

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    raw_dir = os.path.join(outdir, 'raw')
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)

    outlines = []
    done = False
    page = 0
    while not done:
        print("Page", page)
        if page == 0:
            url = domain + initial_target
            index_file = os.path.join(outdir, 'index.html')
        else:
            url = domain + initial_target + '?page=' + str(page)
            index_file = os.path.join(outdir, 'index?page' + str(page) + '.html')

        if os.path.exists(index_file) and not overwrite_index_pages:
            print("Loading index page")
            with open(index_file, 'rb') as f:
                raw_html = f.read()
        else:
            print("Downloading index page")
            raw_html = urllib_get(url)
            time.sleep(sleep)
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
                    output.update(process_speech(domain + link, raw_dir, verbose=False, sleep=sleep, overwrite=overwrite_all))
                    outlines.append(output)

        page += 1
        next_page = initial_target + '?page=' + str(page)
        all_links = html.findAll('a', href=True)
        all_urls = set([link['href'] for link in all_links])
        if next_page not in all_urls:
            done = True

    print("Saving {:d} documents".format(len(outlines)))
    with open(os.path.join(outdir, 'all.jsonlist'), 'w') as fo:
        for line in outlines:
            fo.write(json.dumps(line) + '\n')


def process_speech(url, raw_dir, verbose=False, sleep=2, overwrite=False):
    link_id = url.split('/')[-1]

    speech_file_raw = os.path.join(raw_dir, link_id + '.html')
    if os.path.exists(speech_file_raw) and not overwrite:
        if verbose:
            print("Loading", speech_file_raw)
        with open(speech_file_raw, 'rb') as f:
            raw_speech_html = f.read()
    else:
        if verbose:
            print("Scraping", url)
        raw_speech_html = urllib_get(url)
        time.sleep(sleep)
        with open(speech_file_raw, 'wb') as f:
            f.write(raw_speech_html)
    speech_html = BeautifulSoup(raw_speech_html, 'html.parser')

    title = None
    titles = speech_html.findAll('div', {'class': 'field-ds-doc-title'})
    if len(titles) > 0:
        title_span = titles[0]
        if verbose:
            print("Found title:", title_span)
        headings = title_span.findAll('h1')
        if len(headings) > 0:
            title = headings[0].text

    date = None
    dates = speech_html.findAll('div', {'class': 'field-docs-start-date-time'})
    if len(dates) > 0:
        date_span = dates[0]
        if verbose:
            print("Found date:", date_span)
        spans = date_span.findAll('span', {'class': 'date-display-single'})
        if len(spans) > 0:
            date = spans[0].text

    paragraphs = []
    contents = speech_html.findAll('div', {'class': 'field-docs-content'})
    if len(contents) > 0:
        content = contents[0]
        ps = content.findAll('p')
        for p in ps:
            paragraphs.append(p.text)

    try:
        assert title is not None
        assert date is not None
        
    except AssertionError as e:
        print(link_id)
        print(title)
        print(date)
        print(paragraphs)
        raise e
    output = {'title': title,
              'date': date,
              'text': paragraphs}

    return output
