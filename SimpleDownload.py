from UgeneRepoDownload import *
from DownloadAny import downloadURL, get_modify_date
import os, sys, time, getopt


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    #print 'Number of arguments:', len(sys.argv), 'arguments.'
    #print 'Argument List:', str(sys.argv)

    infile = ''
    outdir = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:")
    except getopt.GetoptError:
        print 'SimpleDownload.py -i <infile> -o <outdir>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'SimpleDownload.py -i <infile> -o <outdir>'
            sys.exit()
        elif opt in ("-i", "--infile"):
            infile = arg
        elif opt in ("-o", "--outdir"):
            outdir = arg

    if not infile:
        print 'SimpleDownload.py -i <infile> -o <outdir>'
        sys.exit()

    home_dir = expanduser("~")

    dest_dir = outdir
    if not dest_dir:
        dest_dir = os.path.join(home_dir, "Downloads")

    print 'Input file is "', infile
    print 'Output dir is "', dest_dir

    time_start = int(time.time())
    list_downloaded = downloadURL(infile, dest_dir)
    time_end = int(time.time())

    time_epapsed = time_end - time_start
    secs = time_epapsed
    mins = time_epapsed / 60
    hours = mins / 60
    days = hours / 24
    hours = hours - days * 24
    mins = mins - (days * 24 + hours) * 60
    secs = secs - (((days * 24 + hours) * 60) + mins) * 60
    print 'Elapsed time:', days, 'days,', hours, 'hours,', mins, 'mins,', secs, 'secs'
    print 'Downloaded data:\n\t', ('\n\t'.join('{}'.format(item) for item in list_downloaded))
