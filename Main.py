import os.path
import requests
import shutil
import hashlib
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class Main:
    def __init__(self):
        self.source = ""
        self.dest = ""

    def validate_file(self, file_path, hash):
        """
        Validates a file against an MD5 hash value

        :param file_path: path to the file for hash validation
        :type file_path:  string
        :param hash:      expected hash value of the file
        :type hash:       string -- MD5 hash value
        """
        m = hashlib.md5()
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(1000 * 1000)  # 1MB
                if not chunk:
                    break
                m.update(chunk)
        return m.hexdigest() == hash

    def download_with_resume(self, url, file_path, hash=None, timeout=10):
        """
        Performs a HTTP(S) download that can be restarted if prematurely terminated.
        The HTTP server must support byte ranges.

        :param file_path: the path to the file to write to disk
        :type file_path:  string
        :param hash: hash value for file validation
        :type hash:  string (MD5 hash value)
        """
        # don't download if the file exists
        if os.path.exists(file_path):
            return
        block_size = 1000 * 1000  # 1MB
        tmp_file_path = file_path + '.part'
        first_byte = os.path.getsize(tmp_file_path) if os.path.exists(tmp_file_path) else 0
        file_mode = 'ab' if first_byte else 'wb'
        logging.debug('Starting download at %.1fMB' % (first_byte / 1e6))
        file_size = -1
        try:
            file_size = int(requests.head(url).headers['Content-length'])
            logging.debug('File size is %s' % file_size)
            headers = {"Range": "bytes=%s-" % first_byte}
            r = requests.get(url, headers=headers, stream=True)
            with open(tmp_file_path, file_mode) as f:
                for chunk in r.iter_content(chunk_size=block_size):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        except IOError as e:
            logging.debug('IO Error - %s' % e)
        finally:
            # rename the temp download file to the correct name if fully downloaded
            if file_size == os.path.getsize(tmp_file_path):
                # if there's a hash value, validate the file
                if hash and not self.validate_file(tmp_file_path, hash):
                    raise Exception('Error validating the file against its MD5 hash')
                shutil.move(tmp_file_path, file_path)
            elif file_size == -1:
                raise Exception('Error getting Content-Length from server: %s' % url)


if __name__ == '__main__':
    my_car = Main()

    if (len(sys.argv) == 3):
        while True:
            my_car.download_with_resume(sys.argv[1], sys.argv[2])



"""
download_with_resume("http://ugene.net/downloads/downloadable_data/taxonomy.7z", "tax.7z")
"""