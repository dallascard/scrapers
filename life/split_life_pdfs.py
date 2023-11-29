import os
from glob import glob
from optparse import OptionParser
from subprocess import call


def main():
    usage = "%prog"
    parser = OptionParser(usage=usage)
    parser.add_option('--basedir', type=str, default='/data/dalc/magazines/life/',
                      help='Data directory: default=%default')


    (options, args) = parser.parse_args()
    basedir = options.basedir

    pdfs = sorted(glob(os.path.join(basedir, '*.pdf')))

    for infile in pdfs[:1]:
        basename = os.path.basename(infile)[:-4]
        # make an output directory for this issue
        outdir = os.path.join(basedir, basename)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        # compress the pdf so individual pages are smaller
        tempfile = os.path.join(outdir, basename + '-temp.pdf')
        cmd = 'gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dNOPAUSE -dQUIET -dBATCH -sOutputFile=%s %s' % (tempfile, infile)
        print(cmd)
        call(cmd, shell=True)
        
        # split the pdf into individual pages
        cmd = 'pdfseparate %s %s-%%d.pdf' % (tempfile, tempfile[:-9])
        print(cmd)
        call(cmd, shell=True)
        
        # remove the temp file
        cmd = 'rm %s' % (tempfile)
        print(cmd)
        call(cmd, shell=True)


if __name__ == '__main__':
    main()
