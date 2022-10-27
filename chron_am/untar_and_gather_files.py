import os
import gzip
import json
import shutil
from glob import glob
from pathlib import Path
from optparse import OptionParser
from collections import defaultdict, Counter
from subprocess import run


# Make a bash script to untar only the .txt files from downloaded tar.bz2 files


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='/u/scr/dcard/data/chron_am',
                      help='Base directory: default=%default')
    parser.add_option('--start', type=int, default=0,
                      help='First file to undar: default=%default')
    parser.add_option('--end', type=int, default=None,
                      help='Last file to undar: default=%default')
    #parser.add_option('--by-issue', action="store_true", default=False,
    #                  help='Divide data by issue: default=%default')

    (options, args) = parser.parse_args()

    basedir = options.basedir
    start = options.start
    end = options.end

    tar_dir = os.path.join(basedir, 'tar_files')
    untarred_dir = os.path.join(basedir, 'untarred')
    if not os.path.exists(untarred_dir):
        os.makedirs(untarred_dir)

    extracted_dir = os.path.join(basedir, 'extracted')
    if not os.path.exists(extracted_dir):
        os.makedirs(extracted_dir)


    files = sorted(glob(os.path.join(tar_dir, '*.bz2')))
    if end is None:
        end = len(files)

    for infile in files[start:end]:
        outlines = []

        filename = os.path.basename(infile)

        command = ['tar', '-xf', infile, '-C', untarred_dir]
        print(' '.join(command))
        run(command)

        # [sn, year, month, day, edition, seq, ocr.txt]
        text_files = sorted(glob(os.path.join(untarred_dir, '*', '*', '*', '*', '*', '*', 'ocr.txt')))
        print(len(text_files))
        
        for text_file in text_files:            
            print(text_file)
            parts = Path(text_file).parts
            print(parts)
            seq = parts[-2].split('-')[1]
            edition = parts[-3].split('-')[1]
            day = parts[-4]
            month = parts[-5]
            year = parts[-6]
            sn = parts[-7]
            with open(text_file) as f:
                text = f.read()
            
            outlines.append({'sn': sn, 'year': int(year), 'month': int(month), 'day': int(day), 'ed': edition, 'seq': seq, 'text': text})

        to_delete = sorted(glob(os.path.join(untarred_dir, '*')))
        for subdir in to_delete:
            print("Deleting", subdir)
            shutil.rmtree(subdir)

        outfile = os.path.join(extracted_dir, filename + '.jsonlist.gz')
        print("Saving {:d} files to {:s}".format(len(outlines), outfile))
        with gzip.open(outfile, 'wt') as f:
            for line in outlines:
                f.write(json.dumps(line) + '\n')


if __name__ == '__main__':
    main()
