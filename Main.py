import os.path
import requests
import shutil
import hashlib
import logging
import sys
from ftpreconnect.ftpReconnect import downloadURL



if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # withMultipart(withReconnect, 'ftp.uniprot.org', 21, '', '', '/pub/databases/uniprot/current_release/uniref/uniref50', 'uniref50.fasta.gz')

    downloadURL('ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref50/uniref50.fasta.gz', logging=logging.ERROR)

    # ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/gi_taxid_nucl.zip
    # withReconnect('ftp.ncbi.nlm.nih.gov', 21, '', '', '/pub/taxonomy', 'gi_taxid_nucl.zip')


