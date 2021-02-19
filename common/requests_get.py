import time
from contextlib import closing

import requests
from requests.exceptions import RequestException
from tqdm import tqdm


def get(url, html_only=True):
    try:
        print("Requesting", url)
        with closing(requests.get(url)) as response:
            if is_good_response(response, html_only=html_only):
                print("Getting content")
                data = response.content
                return data
            else:
                print(response.status_code, response.headers)
                return None
    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def download(url, outfile, binary=True, stream=True, retry=True):
    if binary:
        mode = 'wb'
    else:
        mode = 'w'

    try:
        print("Requesting", url)
        with closing(requests.get(url, stream=stream)) as response:
            if is_good_response(response, html_only=False):
                with open(outfile, mode) as handle:
                    print("Opening", outfile)
                    for data in tqdm(response.iter_content()):
                        handle.write(data)
            else:
                print(response.status_code, response.headers)
                return None
        if retry:
            if response.status_code == 503 or response.status_code == 502:
                # account for system being overloaded by adding a short delay
                time.sleep(2)
                return download(url, outfile, binary, stream, retry=False)
    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(response, html_only=False):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = response.headers['Content-Type'].lower()
    if response.status_code == 200 and content_type is not None:
        if not html_only or content_type.find('html') > -1:
            return True

    return False
