from UgeneRepoDownload import *
from UgeneRepoCreate import *

def sprint_elt(time_elapsed):
    secs = time_elapsed
    mins = time_elapsed / 60
    hours = mins / 60
    days = hours / 24
    hours = hours - days * 24
    mins = mins - (days * 24 + hours) * 60
    secs = secs - (((days * 24 + hours) * 60) + mins) * 60
    return days, hours, mins, secs


if __name__ == '__main__':
    import time

    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    home_dir = expanduser("~")

    work_dir_root = ''
    if not platform.system() == "Linux":
        logging.critical("PLEASE USE LINUX MACHINE WITH HUGE FREE DISK SPACE!")
        exit(-1)
    else:
        work_dir_root = "/opt/share/UGENE-REPO-BUILD"

    download_dir_root = os.path.join(work_dir_root, 'downloads')
    repo_dir_root = os.path.join(work_dir_root, 'repo')
    external_tools_root = '/home/ichebyki/WORKS/ext_tools_linux_64-bit'

    time_start = int(time.time())
    list_downloaded = download_all(download_dir_root, external_tools_root)
    time_end = int(time.time())

    time_elapsed = time_end - time_start
    days, hours, mins, secs = sprint_elt(time_elapsed)
    print 'Download data time:', days, 'days,', hours, 'hours,', mins, 'mins,', secs, 'secs'

    time_start = int(time.time())
    create_all_repo(repo_dir_root, list_downloaded, external_tools_root)
    time_end = int(time.time())

    time_elapsed = time_end - time_start
    days, hours, mins, secs = sprint_elt(time_elapsed)
    print 'Create repo time:', days, 'days,', hours, 'hours,', mins, 'mins,', secs, 'secs'

