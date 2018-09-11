import logging
import sys
from DownloadAny import downloadURL

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    downloadURL('ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref50/uniref50.fasta.gz', "e:\\ichebyki\\Downloads\\")
    downloadURL('ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/gi_taxid_nucl.zip', "e:\\ichebyki\\Downloads\\")
    downloadURL('http://releases.ubuntu.com/16.04/ubuntu-16.04.5-desktop-amd64.iso', "e:\\ichebyki\\Downloads\\")
