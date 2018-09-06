import os.path
import requests
import shutil
import hashlib
import logging
import sys
from shutil import *
from ftpreconnect.ftpReconnect import PyFTPclient as FtpReconnect
from ftpmultipart.ftpMultipart import go as FtpMultipart

def withMultipart(grabber, host, port, login, password, cwd, file):
    FtpMultipart(grabber, host, port, login, password, cwd, file)


def withReconnect(host, port, login, password, cwd, FTP_file):
    obj = FtpReconnect(host, port, login, password)
    obj.setCwd(cwd)
    obj.setBlockSize(8192 * 32)
    obj.setFileName(FTP_file)

    filesize = obj.getFileSize()

    FTP_parts = 8
    chunk_size = filesize / FTP_parts
    last_chunk_size = filesize - (chunk_size * (FTP_parts - 1))

    downloaders = []
    for i in range(FTP_parts):
        if i == (FTP_parts - 1):
            this_chunk_size = last_chunk_size
        else:
            this_chunk_size = chunk_size

        obj = FtpReconnect(host, port, login, password)
        obj.setCwd(cwd)
        obj.setBlockSize(8192 * 32)
        obj.setFileName(FTP_file)
        obj.setLocalName(FTP_file + ".part-" + str(i))
        obj.setChunkStart(chunk_size * i)
        obj.setChunkSize(this_chunk_size)
        obj.downloadFileInThread()

        downloaders.append(obj)

    for downloader in downloaders:
        downloader.thread.join()

    with open(FTP_file, 'w+b') as f:
        for downloader in downloaders:
            copyfileobj(open(downloader.local_filename, 'rb'), f)

    return 1

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # withMultipart(withReconnect, 'ftp.uniprot.org', 21, '', '', '/pub/databases/uniprot/current_release/uniref/uniref50', 'uniref50.fasta.gz')

    withReconnect('ftp.uniprot.org', 21, '', '', '/pub/databases/uniprot/current_release/uniref/uniref50', 'uniref50.fasta.gz')

    # ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/gi_taxid_nucl.zip
    # withReconnect('ftp.ncbi.nlm.nih.gov', 21, '', '', '/pub/taxonomy', 'gi_taxid_nucl.zip')


