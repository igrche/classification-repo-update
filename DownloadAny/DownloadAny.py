import os.path
import requests
import shutil
import hashlib
import logging
import sys
from urlparse import urlparse
from ftpDownloader import ftpDownload
from httpDownloader import httpDownload


def downloadURL(url, dest):
    if os.path.isfile(dest):
        dest = os.path.dirname(dest)
    else:
        if not os.path.isdir(dest):
            os.mkdir(dest)
    path = ''
    o = urlparse(url)
    if o.scheme == 'ftp':
        path = ftpDownload(url, dest)
    elif o.scheme == 'http':
        path = httpDownload(url, dest)
    else:
        return ''
    print('File: {1}\n\twas downloaded\nto: {0}'.format(path, url))
    return path


if __name__ == '__main__':
    pass
