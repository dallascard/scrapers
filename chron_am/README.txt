
Scripts to download newspaper data for Chronicling America from Library of Congress


Updated process:

1. download_batches.py to download all the tar files
2. do_checksums.py to check which downloads are okay
3. untar_and_gather_files.py: untar each file, pull out the text files, and clean up
4. collect_lccns.py: extract lccns from text files
5. download_metadata.py: download associated metadata
6. download_sequence_info.py: use the metadata files to download the sequence info


use download_and_process_ocr.py to download each source, extract text, and put into json

use check_batches.py to download any batches that were missed


TO DO: download the text files for the missing batches



Refactor:
- start by downloading newspaper info (mapped to sns): https://chroniclingamerica.loc.gov/newspapers.json


