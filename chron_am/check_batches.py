import os
import json
import shutil
import datetime as dt
from glob import glob
from optparse import OptionParser
from collections import defaultdict, Counter
from subprocess import run

from tqdm import tqdm
from common.requests_get import download, get


# Download the index file for OCR batches, and write a bash script to download using wget

def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='/u/scr/dcard/data/chron_am',
                      help='Base directory: default=%default')
    #parser.add_option('--logfile', type=str, default='errors.txt',
    #                  help='Logfile location (in basedir): default=%default')
    #parser.add_option('--start', type=int, default=0,
    #                  help='First file: default=%default')
    #parser.add_option('--end', type=int, default=1,
    #                  help='Last file: default=%default')
    parser.add_option('--no-overwrite', action="store_true", default=False,
                      help="Don't overwrite batch files: default=%default")


    (options, args) = parser.parse_args()

    basedir = options.basedir
    overwrite = not options.no_overwrite
    #error_log = os.path.join(basedir, options.logfile)
    #start_date = options.start_date
    #start = options.start
    #end = options.end

    #indexed_dir = os.path.join(basedir, 'indexed')
    batches_dir = os.path.join(basedir, 'batches')
    tarfile_dir = os.path.join(basedir, 'tar_files')
    json_dir = os.path.join(basedir, 'extra_jsons')

    if not os.path.exists(batches_dir): 
        os.makedirs(batches_dir)

    if not os.path.exists(json_dir): 
        os.makedirs(json_dir)

    done = False
    batch_file_num = 1
    first_target_url = 'https://chroniclingamerica.loc.gov/batches/{:d}.json'.format(batch_file_num)
    target_url = first_target_url

    #batches_per_lccn = Counter()

    print("Downloading batch metadata")
    while not done:        
        target_num = int(os.path.basename(target_url).split('.')[0])
        try:
            assert target_num == batch_file_num
        except AssertionError as e:
            print("Mismatch on batch num!", target_url, batch_file_num)
            raise e

        outfile = os.path.join(batches_dir, str(batch_file_num) + '.json')        
        if not os.path.exists(outfile) or overwrite:
            download(target_url, outfile)

        with open(outfile, 'r') as f:
            data = json.load(f)

        batches = data['batches']
        print(target_url, len(batches))
        for b_i, batch in enumerate(batches):
            name = batch['name']
            batch_url = batch['url']
            expected_page_count = int(batch['page_count'])
            lccns = batch['lccns']
            #batches_per_lccn.update(lccns)
            #print('\t' + name, lccns, expected_page_count)

            logfile = os.path.join(tarfile_dir, name + '.tar.bz2.log')            
            if not os.path.exists(logfile):
                print('\t' + logfile, 'not found!')                
                outfile = os.path.join(json_dir, name + '.json')
                if not os.path.exists(outfile) or overwrite:
                    print("Downloading", name)
                    download(batch_url, outfile)
                

        if 'next' in data:
            batch_file_num += 1
            target_url = data['next']
        else:
            done = True


if __name__ == '__main__':
    main()
