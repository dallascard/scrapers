import os
import sys
import json
import time
from optparse import OptionParser
from collections import defaultdict, Counter

from common.requests_get import get_with_status


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--outdir', type=str, default='data/nyt/archive/',
                      help='Output directory: default=%default')
    parser.add_option('--start-year', type=int, default=1851,
                      help='Start year: default=%default')
    parser.add_option('--last-year', type=int, default=2021,
                      help='Start year: default=%default')
    parser.add_option('--start-month', type=int, default=1,
                      help='Start month: default=%default')
    parser.add_option('--sleep', type=int, default=3,
                      help='Time to sleep after each request: default=%default')
    parser.add_option('--api-file', type=str, default='api_keys/nyt.txt',
                      help='Location of file containing your NYT API key: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    outdir = options.outdir
    start_year = options.start_year
    last_year = options.last_year
    start_month = options.start_month
    sleep = options.sleep
    key_file = options.api_file

    if not os.path.exists(key_file):
        raise FileNotFoundError("API key file not found at:", key_file)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    with open(key_file) as f:
        lines = f.readlines()
    key = lines[0].strip()

    year = start_year
    month = start_month

    while year <= last_year:
        while month < 13:
            url = f'https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={key}'
            response = get_with_status(url, html_only=False, retry=True)
            data = response.content
            status = response.status_code
            if status != 200 or data is None:
                print(f"Last requested: {year}.{month}")
                print(f"Exiting with status {status}")
                sys.exit()
            else:
                data = json.loads(data)
                if 'response' in data and 'docs' in data['response']:
                    response = data['response']
                    if 'docs' in response and len(response['docs']) > 0:
                        n_docs = len(response['docs'])
                        print(f'Saving {n_docs} from {year}.{month}')
                        outfile = os.path.join(outdir, f'{year}.{month}.json')
                        with open(outfile, 'w') as f:
                            json.dump(response, f, indent=2)

            time.sleep(sleep)
            month += 1
        year += 1
        month = 1


if __name__ == '__main__':
    main()
