import os.path
import requests
import shutil
import hashlib
import logging
import sys
from ftpreconnect.ftpReconnect import downloadURL
from pySmartDL import SmartDL


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    #downloadURL('ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref50/uniref50.fasta.gz', logging=logging.ERROR)
    # ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/gi_taxid_nucl.zip

    url = "http://releases.ubuntu.com/16.04/ubuntu-16.04.5-desktop-amd64.iso"
    dest = "e:\\ichebyki\\Downloads\\" # or '~/Downloads/' on linux
    obj = SmartDL(url, dest, progress_bar=False, threads=50)
    obj.start()
    # [*] 0.23 Mb / 0.37 Mb @ 88.00Kb/s [##########--------] [60%, 2s left]
    path = obj.get_dest()
    logging.info('File {0} was downloaded to {1}'.format(url, path))
    logging.info(obj.get_status())
    logging.info(obj.get_progress())
