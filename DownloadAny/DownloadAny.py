import os.path
import requests
import shutil
import hashlib
import logging
import sys
from urlparse import urlparse
from ftpDownloader import ftpDownload
from ftpDownloader import ftp_get_modify_date
from httpDownloader import httpDownload, httpsDownload

def make_dest_dir(dir):
    if os.path.isfile(dir):
        dir = os.path.dirname(dir)
    else:
        if not os.path.isdir(dir):
            os.makedirs(dir)
    return dir


def downloadURL(url, dest, mask=None, mask2=None):
    dest = make_dest_dir(dest)

    path = ''
    o = urlparse(url)
    if o.scheme == 'ftp':
        path = ftpDownload(url, dest, mask, mask2)
    elif o.scheme == 'http':
        path = httpDownload(url, dest, mask, mask2)
    elif o.scheme == 'https':
        path = httpsDownload(url, dest, mask, mask2)
    else:
        return ''

    return path


def get_modify_date(url):
    o = urlparse(url)
    if o.scheme == 'ftp':
        return ftp_get_modify_date(url)
    elif o.scheme == 'http':
        return None
    else:
        return None


if __name__ == '__main__':
    pass
