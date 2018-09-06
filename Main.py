import os.path
import requests
import shutil
import hashlib
import logging
import sys
from ftpreconnect.ftpReconnect import PyFTPclient as FtpReconnect
from ftpmultipart.ftpMultipart import go as FtpMultipart

def withMultipart(grabber, host, port, login, password, cwd, file):
    FtpMultipart(grabber, host, port, login, password, cwd, file)


def withReconnect(host, port, login, password, cwd, file):
    obj = FtpReconnect(host, port, login, password)
    obj.setCwd(cwd)
    obj.DownloadFile(file)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # withMultipart(withReconnect, 'ftp.uniprot.org', 21, '', '', '/pub/databases/uniprot/current_release/uniref/uniref50', 'uniref50.fasta.gz')

    # withReconnect('ftp.uniprot.org', 21, '', '', '/pub/databases/uniprot/current_release/uniref/uniref50', 'uniref50.fasta.gz')

    # ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/gi_taxid_nucl.zip
    withReconnect('ftp.ncbi.nlm.nih.gov', 21, '', '', '/pub/taxonomy', 'gi_taxid_nucl.zip')


