from optparse import OptionParser

from app.common import scrape_documents


def main():
    usage = "%prog\n" \
            "Scrape miscellaneous remarks from the American Presidency Project"
    parser = OptionParser(usage=usage)
    parser.add_option('--outdir', type=str, default='data/app/misc_remarks/',
                      help='Output directory): default=%default')
    parser.add_option('--sleep', type=int, default=2,
                      help='Seconds to sleep after downloading a page: default=%default')
    parser.add_option('--overwrite', action="store_true", default=False,
                      help='Overwrite index pages: default=%default')
    parser.add_option('--overwrite-all', action="store_true", default=False,
                      help='Overwrite index and document pages: default=%default')

    (options, args) = parser.parse_args()

    outdir = options.outdir
    overwrite = options.overwrite
    overwrite_all = options.overwrite_all
    sleep = options.sleep

    domain = 'https://www.presidency.ucsb.edu'
    initial_target = '/documents/app-categories/presidential/miscellaneous-remarks'

    scrape_documents(initial_target, outdir, overwrite_index_pages=overwrite, overwrite_all=overwrite_all, sleep=sleep, domain=domain)


if __name__ == '__main__':
    main()
