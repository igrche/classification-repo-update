import logging
import sys
import platform
from DownloadAny import downloadURL

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    dest_dir = ''
    if platform.system() == "Windows":
        dest_dir = "e:\\ichebyki\\Downloads\\"
    else:
        dest_dir = "/home/ichebyki/Downloads"

    downloadURL('ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref50/uniref50.fasta.gz',
                dest_dir)
    downloadURL('ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/gi_taxid_nucl.zip',
                dest_dir)
    downloadURL('http://releases.ubuntu.com/16.04/ubuntu-16.04.5-desktop-amd64.iso',
                dest_dir)
