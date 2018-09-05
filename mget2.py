import argparse
import logging
import Queue
import os
import requests
import signal
import sys
import time
import threading
import utils as _fdUtils

DESKTOP_PATH = os.path.expanduser("~/Desktop")

appName = 'FileDownloader'

logFile = os.path.join(DESKTOP_PATH, '%s.log' % appName)

_log = _fdUtils.fdLogger(appName, logFile, logging.DEBUG, logging.DEBUG, console_level=logging.DEBUG)

queue = Queue.Queue()
STOP_REQUEST = threading.Event()
maxSplits = threading.BoundedSemaphore(3)
threadLimiter = threading.BoundedSemaphore(5)
lock = threading.Lock()

pulledSize = 0
dataDict = {}

def _grabAndWriteToDisk(threadId, split, url, saveTo, first=None, queue=None, mode='wb', irange=None):
    """ Function to download file when single chunk..

        Args:
            url(str): url of file to download
            saveTo(str): path where to save file
            first(int): starting byte of the range
            queue(Queue.Queue): queue object to set status for file download
            mode(str): mode of file to be downloaded
            irange(str): range of byte to download

    """
    fileName = url.split('/')[-1]
    filePath = os.path.join(saveTo, fileName)
    fileSize = int(_fdUtils.getUrlSizeInBytes(url))
    downloadedFileSize = 0 if not first else first
    block_sz = 8192
    resp = requests.get(url, headers={'Range': 'bytes=%s' % irange}, stream=True)
    for fileBuffer in resp.iter_content(block_sz):
        if not fileBuffer:
            break

        with open(filePath, mode) as fd:
            downloadedFileSize += len(fileBuffer)
            fd.write(fileBuffer)
            mode = 'a'

            status = r"%10d  [%3.2f%%]" % (downloadedFileSize, downloadedFileSize * 100. / fileSize)
            status = status + chr(8)*(len(status)+1)
            sys.stdout.write('%s\r' % status)
            time.sleep(.01)
            sys.stdout.flush()
            if downloadedFileSize == fileSize:
                STOP_REQUEST.set()
                queue.task_done()
                _log.info("Download Completed %s%% for file %s, saved to %s",
                    downloadedFileSize * 100. / fileSize, fileName, saveTo)


def _downloadChunk(url, idx, irange, pulledSize, fileName, sizeInBytes):
    resp = requests.get(url, headers={'Range': 'bytes=%s' % irange}, stream=True)
    chunk_size = irange.split("-")[-1]
    for chunk in resp.iter_content(chunk_size):
        status = r"%10d  [%3.2f%%]" % (pulledSize, pulledSize * 100. / int(chunk_size))
        status = status + chr(8)*(len(status)+1)
        sys.stdout.write('%s\r' % status)
        sys.stdout.flush()
        pulledSize += len(chunk)
        dataDict[idx] = chunk
        time.sleep(.03)
        if pulledSize == sizeInBytes:
            _log.info("%s downloaded %3.0f%%", fileName, pulledSize * 100. / sizeInBytes)

class ThreadedFetch(threading.Thread):
    """ docstring for ThreadedFetch
    """
    def __init__(self, queue):
        super(ThreadedFetch, self).__init__()
        self.queue = queue
        self.lock = threading.Lock()

    def run(self):
        threadLimiter.acquire()
        try:
            items = self.queue.get()
            url = items[0]
            saveTo = DESKTOP_PATH if not items[1] else items[1]
            split = items[-1]

            # grab split chunks in separate thread.
            if split > 1:
                maxSplits.acquire()
                try:
                    fileName = url.split('/')[-1]
                    sizeInBytes = int(_fdUtils.getUrlSizeInBytes(url))
                    byteRanges = _fdUtils.getRange(sizeInBytes, split)
                    filePath = os.path.join(saveTo, fileName)

                    downloaders = [
                        threading.Thread(
                            target=_downloadChunk,
                            args=(url, idx, irange, int(irange.split('-')[0]), fileName, sizeInBytes),
                        )
                        for idx, irange in enumerate(byteRanges)
                        ]

                    # start threads, let run in parallel, wait for all to finish
                    for th in downloaders:
                        th.start()

                    # this makes the wait for all thread to finish
                    # which confirms the dataDict is up-to-date
                    for th in downloaders:
                        th.join()
                    downloadedSize = 0
                    with open(filePath, 'wb') as fh:
                        for _idx, chunk in sorted(dataDict.iteritems()):
                            downloadedSize += len(chunk)
                            status = r"%10d  [%3.2f%%]" % (downloadedSize, downloadedSize * 100. / sizeInBytes)
                            status = status + chr(8)*(len(status)+1)
                            fh.write(chunk)
                            sys.stdout.write('%s\r' % status)
                            time.sleep(.04)
                            sys.stdout.flush()
                            if downloadedSize == sizeInBytes:
                                _log.info("%s, saved to %s", fileName, saveTo)
                    self.queue.task_done()
                finally:
                    maxSplits.release()

            else:
                while not STOP_REQUEST.isSet():
                    self.setName("primary_%s" % url.split('/')[-1])
                    # if downlaod whole file in single chunk no need
                    # to start a new thread, so directly download here.
                    _grabAndWriteToDisk(None, split, url, saveTo, 0, self.queue)
        finally:
            threadLimiter.release()


def main(appName):

    args = _fdUtils.getParser()
    urls_saveTo = {}

    # spawn a pool of threads, and pass them queue instance
    # each url will be downloaded concurrently
    for i in xrange(len(args.urls)):
        t = ThreadedFetch(queue)
        t.daemon = True
        t.start()

    split = 3
    try:
        for url in args.urls:
            urls_saveTo[url] = args.saveTo

        # populate queue with data
        for url, saveTo in urls_saveTo.iteritems():
            queue.put((url, saveTo, split))

        # wait on the queue until everything has been processed
        queue.join()
        _log.info('Finsihed all dowonloads.')
    except (KeyboardInterrupt, SystemExit):
        _log.critical('Received keyboard interrupt, quitting threads.')
