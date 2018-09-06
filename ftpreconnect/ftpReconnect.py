# coding=utf-8
__author__ = 'Roman Podlinov'

import threading
import logging
import ftplib
import socket
import time
import sys
import os
from threading import *


def setInterval(interval, times = -1):
    # This will be the actual decorator,
    # with fixed interval and times parameter
    def outer_wrap(function):
        # This will be the function to be
        # called
        def wrap(*args, **kwargs):
            stop = threading.Event()

            # This is another function to be executed
            # in a different thread to simulate setInterval
            def inner_wrap():
                i = 0
                while i != times and not stop.isSet():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap


class Done(Exception):
    pass


class PyFTPclient:

    thread_number = 0

    def __init__(self, host, port, login, passwd, monitor_interval = 30):
        self.host = host
        self.port = port
        self.login = login
        self.passwd = passwd
        self.monitor_interval = monitor_interval
        self.ptr = None
        self.max_attempts = 15
        self.waiting = True
        self.cwd = "/"
        self.dst_filesize = 0
        self.f = None
        self.local_filename = None
        self.block_size = 8192
        self.fileName = None
        self.chunkStart = 0
        self.chunkSize = -1
        self.thread_number = None
        self.thread = None


    def setLocalName(self, local_file_name):
        self.local_filename = local_file_name

    def setChunkStart(self, param):
        self.chunkStart = param

    def setChunkSize(self, param):
        self.chunkSize = param

    def setBlockSize(self, size=8192):
        self.block_size = size

    def setCwd(self, dir="/"):
        self.cwd = dir


    def setFileName(self, file):
        self.fileName = file

    def on_data(self, data):
        self.f.write(data)
        if self.f.tell() >= self.dst_filesize:
            raise Done

    def downloadFileInThread(self):
        PyFTPclient.thread_number += 1
        self.thread_number = PyFTPclient.thread_number
        self.thread = Thread(target=self.downloadFile)
        self.thread.start()

    def connect(self, ftp):
        ftp.connect(self.host, self.port)
        ftp.login(self.login, self.passwd)
        # optimize socket params for download task
        ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)
        # ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
        ftp.cwd(self.cwd)

    def downloadFile(self):
        res = ''
        if self.local_filename is None:
            self.local_filename = self.fileName

        with open(self.local_filename, 'w+b') as f:
            self.f = f
            self.ptr = self.f.tell()

            @setInterval(self.monitor_interval)
            def monitor():
                if not self.waiting:
                    i = self.f.tell()
                    if self.ptr < i:
                        logging.debug("%d  -  %0.1f Kb/s" % (i, (i-self.ptr)/(1024*self.monitor_interval)))
                        self.ptr = i
                    else:
                        ftp.close()



            ftp = ftplib.FTP()
            ftp.set_debuglevel(2)
            ftp.set_pasv(True)

            self.connect(ftp)
            ftp.voidcmd('TYPE I')
            if self.chunkSize == -1:
                self.dst_filesize = ftp.size(self.fileName)
            else:
                self.dst_filesize = self.chunkSize

            mon = monitor()
            while self.dst_filesize > self.f.tell():
                try:
                    self.connect(ftp)
                    self.waiting = False
                    # retrieve file from position where we were disconnected
                    res = ftp.retrbinary('RETR %s' % self.fileName, self.on_data, blocksize=self.block_size, rest=self.chunkStart) if self.f.tell() == 0 \
                        else ftp.retrbinary('RETR %s' % self.fileName, self.on_data, blocksize=self.block_size, rest=self.chunkStart + self.f.tell())

                except Done:
                    break

                except:
                    self.waiting = True
                    self.max_attempts -= 1
                    if self.max_attempts <= 0:
                        mon.set()
                        logging.exception('')
                        logging.info('ERROR: ftp RETR error')
                        raise
                    logging.info('waiting 30 sec...')
                    time.sleep(30)
                    logging.info('reconnect')

            self.waiting = True
            mon.set() #stop monitor
            ftp.close()

            if not res.startswith('226 Transfer complete'):
                if not self.f.tell() >= self.dst_filesize:
                    logging.error('Downloaded file {0} is not full.'.format(self.fileName))
                    # os.remove(self.local_filename)
                    return None

            if self.f.tell() > self.dst_filesize:
                logging.info('Downloaded file size of {0} is {1}.'.format(self.fileName, self.f.tell()))
                self.f.truncate(self.dst_filesize)
                logging.info("\tAfter trancating the file size is {0}.".format(os.path.getsize(self.local_filename)))

                return 1
            else:
                return None

    def getFileSize(self):
        ftp = ftplib.FTP()
        ftp.set_debuglevel(2)
        ftp.set_pasv(True)

        self.connect(ftp)
        ftp.voidcmd('TYPE I')
        filesize = ftp.size(self.fileName)
        ftp.quit()
        return filesize


if __name__ == "__main__":
    # logging.basicConfig(filename='/var/log/dreamly.log',format='%(asctime)s %(levelname)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=cfg.logging.level)
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # obj = PyFTPclient('ftp.uniprot.org', 21, '', '')
    # obj.setCwd('/pub/databases/uniprot/current_release/uniref/uniref50')
    # obj.DownloadFile('uniref50.fasta.gz')

    # ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/gi_taxid_nucl.zip
    obj = PyFTPclient('ftp.ncbi.nlm.nih.gov', 21, '', '')
    obj.setCwd('/pub/taxonomy')
    obj.DownloadFile('gi_taxid_nucl.zip')
