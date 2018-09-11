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
    path = ''
    o = urlparse(url)
    if o.scheme == 'ftp':
        path = ftpDownload(url, dest)
    elif o.scheme == 'http':
        path = httpDownload(url, dest)
    print('File {1} was downloaded to {0}'.format(path, url))
    return path


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    downloadURL('ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref50/uniref50.fasta.gz',
                "e:\\ichebyki\\Downloads\\")
    downloadURL('ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/gi_taxid_nucl.zip',
                "e:\\ichebyki\\Downloads\\")
    downloadURL('http://releases.ubuntu.com/16.04/ubuntu-16.04.5-desktop-amd64.iso',
                "e:\\ichebyki\\Downloads\\")
