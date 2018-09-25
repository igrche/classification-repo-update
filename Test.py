from UgeneRepoDownload import *

if __name__ == '__main__':
    import time

    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    home_dir = expanduser("~")

    dest_dir = ''
    if platform.system() == "Windows":
        dest_dir = "e:\\ichebyki\\Downloads"
    else:
        dest_dir = "/home/ichebyki/Downloads"

    dest_dir = os.path.join(dest_dir, 'UGENE-REPO')
    time_start = int(time.time())
    list_downloaded = download_all(dest_dir, '/home/ichebyki/WORKS/ext_tools_linux_64-bit')
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
