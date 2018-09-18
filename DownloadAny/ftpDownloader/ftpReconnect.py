# coding=utf-8
__author__ = 'Roman Podlinov'

import threading
import functools
import logging
import ftplib
import socket
import time
import sys
import os
import random
from threading import Thread
from urlparse import urlparse
from shutil import copyfileobj


__version_mjaor__ = 0
__version_minor__ = 0
__version_micro__ = 1
__version__ = "%d.%d.%d" % (__version_mjaor__, __version_minor__, __version_micro__)


def setInterval(interval, times=-1):
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


def synchronized(wrapped):
    lock = threading.Lock()

    @functools.wraps(wrapped)
    def _wrap(*args, **kwargs):
        with lock:
            return wrapped(*args, **kwargs)
    return _wrap


class Done(Exception):
    pass


class PyFTPclient:

    thread_number = 0
    ave_speed = {'chunks': 0, 'speed': 0, 'last_speed': 0}
    wait_for_free_socket_timeout = 60

    def __init__(self, host, port, login, passwd, monitor_interval=30, logging_level=logging.ERROR):
        logging.basicConfig(stream=sys.stdout, level=logging_level)

        self.logging_level = logging_level
        self.ftp = None
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
        self.wait_for_free_socket = False

    @synchronized
    def update_ave_speed(self, speed):
        chunks = PyFTPclient.ave_speed['chunks']
        PyFTPclient.ave_speed['last_speed'] = speed
        PyFTPclient.ave_speed['speed'] = (PyFTPclient.ave_speed['speed'] * chunks + speed) / (chunks + 1)
        PyFTPclient.ave_speed['chunks'] = chunks + 1
        if self.chunkSize == -1:
            PyFTPclient.wait_for_free_socket_timeout = 60
        else:
            PyFTPclient.wait_for_free_socket_timeout = self.chunkSize / PyFTPclient.ave_speed['speed'] / 2

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
        return self.thread

    def disconnect(self, message):
        try:
            self.ftp.quit()
        except Exception, e:
            logging.debug("---- {1}: disconnect: self.ftp.quit() exception: {0}".format(e.message, message))
        self.ftp = None

    def connect(self, message):
        logging.info('{0}: try to connect'.format(message))
        self.ftp = ftplib.FTP()
        try_count = 16
        i = 0
        while i < try_count:
            try:
                self.ftp.connect(self.host, self.port, timeout=15)
                self.ftp.set_debuglevel(2 if self.logging_level == logging.DEBUG
                                        else 1 if self.logging_level == logging.INFO else 0)
                self.ftp.login(self.login, self.passwd)
                # optimize socket params for download task
                self.ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                # self.ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)
                # self.ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
                break
            except Exception, e:
                if e.message == '421 There are too many connections from your internet address.' or \
                        e.message == '530 Sorry, you have exceeded the number of connections.':
                    self.wait_for_free_socket = True
                    logging.info(e.message)
                    sleep_time = PyFTPclient.wait_for_free_socket_timeout \
                            + (PyFTPclient.wait_for_free_socket_timeout * random.randint(0, 21) / 50) \
                            - PyFTPclient.wait_for_free_socket_timeout / 5
                    logging.info('{1}: Waiting free sockets for {0} sec ({2} out of {3})...'.format(sleep_time, message, i, try_count))
                    time.sleep(sleep_time)
                    i = i + 1
                    self.wait_for_free_socket = False
                else:
                    logging.error('{1}: Failed to connect + login + cwd: {0}'.format(e.message, message))
                    raise

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
                    if self.wait_for_free_socket:
                        logging.info("---- monitor: wait for free socket")
                        pass
                    else:
                        i = self.f.tell()
                        if self.ptr < i:
                            speed = (i - self.ptr)/(1024 * self.monitor_interval)
                            logging.debug("%d  -  %0.1f Kb/s" % (i, speed))
                            self.ptr = i
                            self.update_ave_speed(speed * 1024)

                        else:
                            self.disconnect('monitor')

            self.waiting = True
            if self.chunkSize == -1:
                self.dst_filesize = self.getFileSize()
            else:
                self.dst_filesize = self.chunkSize

            self.ftp = ftplib.FTP()

            mon = monitor()
            while self.dst_filesize > self.f.tell():
                try:
                    self.connect('downloadFile (loop)')
                    self.ftp.cwd(self.cwd)
                    self.ftp.set_pasv(True)
                    self.ftp.voidcmd('TYPE I')
                    self.waiting = False
                    self.wait_for_free_socket = False
                    res = self.ftp.retrbinary('RETR %s' % self.fileName, self.on_data, blocksize=self.block_size, rest=self.chunkStart + self.f.tell())

                except Done:
                    self.waiting = True
                    break

                except Exception, e:
                    self.waiting = True
                    self.max_attempts -= 1
                    if self.max_attempts <= 0:
                        mon.set()
                        logging.exception('')
                        raise

                    logging.debug('{1}: ERROR: self.ftp RETR error: {0}'.format(e.message, 'downloadFile (loop)'))
                    logging.info('{1}: waiting {0} sec...'.format(self.monitor_interval, 'downloadFile (loop)'))
                    time.sleep(self.monitor_interval)

            mon.set()   # stop monitor
            self.disconnect('downloadFile')

            if not res.startswith('226 Transfer complete'):
                if not self.f.tell() >= self.dst_filesize:
                    logging.critical('Downloaded file {0} is not full.'.format(self.local_filename))
                    # os.remove(self.local_filename)
                    return None

            if self.f.tell() > self.dst_filesize:
                logging.info('Downloaded file size of {0} is {1}.'.format(self.local_filename, self.f.tell()))
                self.f.truncate(self.dst_filesize)
                logging.info("After trancating the file size is {0}.".format(os.path.getsize(self.local_filename)))

            logging.info('---------------------- Downloaded file size of {0} is {1}.'.format(self.local_filename, self.f.tell()))
            return 1

    def getFileSize(self):
        self.connect('getFileSize')
        self.ftp.cwd(self.cwd)
        self.ftp.set_pasv(True)
        self.ftp.voidcmd('TYPE I')
        filesize = self.ftp.size(self.fileName)
        self.disconnect('getFileSize')
        return filesize

def ftp_get_modify_date(url):
    o = urlparse(url)
    FTP_host = o.hostname
    FTP_port = int(o.port) if o.port else 21
    FTP_login = o.username if o.username else ''
    FTP_password = o.password if o.password else ''
    FTP_path = o.path
    FTP_cwd = os.path.dirname(FTP_path)
    FTP_file = os.path.basename(FTP_path)

    ftp = ftplib.FTP()
    ftp.connect(FTP_host, FTP_port)
    ftp.login(FTP_login, FTP_password)
    ftp.cwd(FTP_cwd)
    modifiedTime = ftp.sendcmd('MDTM ' + FTP_file)
    # successful response: '213 20120222090254'
    ftp.quit()

    from datetime import datetime
    return modifiedTime[4:8] + '-' + modifiedTime[8:10] + '-' + modifiedTime[10:12]


def ftpDownload(url, dest, mim_size=26214400, chunk_size=104857600, logging_level=logging.ERROR):
    logging.basicConfig(stream=sys.stdout, level=logging_level)

    o = urlparse(url)
    FTP_host = o.hostname
    FTP_port = int(o.port) if o.port else 21
    FTP_login = o.username if o.username else ''
    FTP_password = o.password if o.password else ''
    FTP_path = o.path
    FTP_cwd = os.path.dirname(FTP_path)
    FTP_file = os.path.basename(FTP_path)
    FTP_parts = 80

    obj = PyFTPclient(FTP_host, FTP_port, FTP_login, FTP_password, logging_level=logging_level)
    obj.setCwd(FTP_cwd)
    obj.setBlockSize(8192)
    obj.setFileName(FTP_file)

    filesize = obj.getFileSize()

    if filesize < mim_size:
        FTP_parts = 1
    else:
        FTP_parts = filesize / chunk_size
        if FTP_parts < 1:
            FTP_parts = 1
    chunk_size = filesize / FTP_parts
    last_chunk_size = filesize - (chunk_size * (FTP_parts - 1))

    downloaders = []
    for i in range(FTP_parts):
        if i == (FTP_parts - 1):
            this_chunk_size = last_chunk_size
        else:
            this_chunk_size = chunk_size

        obj = PyFTPclient(FTP_host, FTP_port, FTP_login, FTP_password, logging_level=logging_level)
        obj.setCwd(FTP_cwd)
        obj.setBlockSize(8192 * 32)
        obj.setFileName(FTP_file)
        obj.setLocalName(dest + os.sep + FTP_file + ".%.3d" % i)
        obj.setChunkStart(chunk_size * i)
        obj.setChunkSize(this_chunk_size)
        obj.downloadFileInThread()

        downloaders.append(obj)

    for downloader in downloaders:
        downloader.thread.join()

    if os.path.isdir(dest):
        dest = os.path.abspath(dest) + os.path.sep + FTP_file
    with open(dest, 'w+b') as f:
        for downloader in downloaders:
            copyfileobj(open(downloader.local_filename, 'rb'), f)
            os.remove(downloader.local_filename)
    return dest


if __name__ == "__main__":
    # logging.basicConfig(filename='/var/log/dreamly.log',format='%(asctime)s %(levelname)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=cfg.logging.level)
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    pass
