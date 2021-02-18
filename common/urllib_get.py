from urllib.request import urlopen
from contextlib import closing

# Sometimes urllib works better than requests


def urllib_get(url):
    try:
        with closing(urlopen(url)) as response:
            if is_good_response(response):
                return response.read()
            else:
                print(response)
                return None

    except Exception as e:
        print('Error during request to {0} : {1}'.format(url, str(e)))


def is_good_response(response):
    content_type = response.headers['Content-Type'].lower()
    return (response.status == 200
            and content_type is not None
            and content_type.find('html') > -1)