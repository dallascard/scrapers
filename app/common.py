import os
import re
import time

from bs4 import BeautifulSoup
from common.urllib_get import urllib_get


def process_speech(url, raw_dir, verbose=False, sleep=2):
    link_id = url.split('/')[-1]

    speech_file_raw = os.path.join(raw_dir, link_id + '.html')
    if os.path.exists(speech_file_raw):
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

    assert title is not None
    assert date is not None
    output = {'title': title,
              'date': date,
              'text': paragraphs}

    return output
