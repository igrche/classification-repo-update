import os.path
import requests
import shutil
import hashlib
import logging
import sys
from urlparse import urlparse
from ftpDownloader import ftpDownload
from ftpDownloader import ftp_get_modify_date
from httpDownloader import httpDownload


def downloadURL(url, dest):
    if os.path.isfile(dest):
        dest = os.path.dirname(dest)
    else:
        if not os.path.isdir(dest):
            os.makedirs(dest)
    path = ''
    o = urlparse(url)
    if o.scheme == 'ftp':
        path = ftpDownload(url, dest)
    elif o.scheme == 'http':
        path = httpDownload(url, dest)
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
