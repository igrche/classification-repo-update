# coding=utf-8
import logging
import sys
import platform
import tempfile
import os
import xml.etree.ElementTree as ET
import re
from os.path import expanduser
from DownloadAny import downloadURL

work_dir = ''
if platform.system() == "Windows":
    work_dir = "e:\\ichebyki\\Downloads\\"
else:
    work_dir = "/home/ichebyki/Downloads"

def xml_to_dict(node):
    u'''
    @param node:lxml_node
    @return: dict
    '''

    return {
        'tag': node.tag,
        'text': node.text,
        'attrib': node.attrib,
        'children': {
            child.tag: xml_to_dict(child) for child in node
        }
    }

def do_ngs_classification_clark_bacterial_viral_database(element):
    dict = xml_to_dict(element)
    Name = dict['children']['Name']['text']
    Dependencies = dict['children']['Dependencies']['text']
    Version = dict['children']['Version']['text']
    ReleaseDate = dict['children']['ReleaseDate']['text']
    DownloadableArchives = dict['children']['DownloadableArchives']['text']
    Script = dict['children']['Script']['text']
    OS = dict['children']['UpdateFile']['attrib']['OS']
    CompressedSize = dict['children']['UpdateFile']['attrib']['CompressedSize']
    UncompressedSize = dict['children']['UpdateFile']['attrib']['UncompressedSize']
    SHA1 = dict['children']['SHA1']['text']


def do_ngs_classification_diamond_uniref50_database(element):
    ugene_dict = xml_to_dict(element)
    ugene_Name = ugene_dict['children']['Name']['text']
    ugene_Dependencies = ugene_dict['children']['Dependencies']['text']
    ugene_Version = ugene_dict['children']['Version']['text']
    ugene_ReleaseDate = ugene_dict['children']['ReleaseDate']['text']
    ugene_DownloadableArchives = ugene_dict['children']['DownloadableArchives']['text']
    ugene_Script = ugene_dict['children']['Script']['text']
    ugene_OS = ugene_dict['children']['UpdateFile']['attrib']['OS']
    ugene_CompressedSize = ugene_dict['children']['UpdateFile']['attrib']['CompressedSize']
    ugene_UncompressedSize = ugene_dict['children']['UpdateFile']['attrib']['UncompressedSize']
    ugene_SHA1 = ugene_dict['children']['SHA1']['text']

    remote_uniref50_RELEASE_metalink = 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref50/RELEASE.metalink'
    remote_uniref50_fasta_gz = 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref50/uniref50.fasta.gz'
    remote_prot_accession2taxid_gz = 'ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.gz'
    remote_prot_accession2taxid_gz_md5 = 'ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.gz.md5'

    work_dir_uniref50 = os.path.join(work_dir, 'uniref50')
    download_uniref50_RELEASE_metalink = downloadURL(remote_uniref50_RELEASE_metalink, work_dir_uniref50)
    download_uniref50_RELEASE_metalink_tree = ET.parse(download_uniref50_RELEASE_metalink)
    root = download_uniref50_RELEASE_metalink_tree.getroot()

    remote_Version = root.findall('.//{http://www.metalinker.org/}version')[0].text

    ugene_ReleaseDate_array = re.split(r"_|-", ugene_ReleaseDate)
    remote_Version_array = re.split(r"_|-", remote_Version)

    result = False
    if (ugene_ReleaseDate_array[0] < remote_Version_array[0]):
        result = True
    if (ugene_ReleaseDate_array[1] < remote_Version_array[1]):
        result = True

    return result

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    home_dir = expanduser("~")
    work_dir = os.path.join(tempfile.gettempdir(), 'classification-repo-update-work')

    '''
    1) Скачать файл Updates.xml.
    2) Вытащить из него текущие версии нужных компонентов
    '''
    updates_xml_url = 'http://ugene.net/downloads/installer_repositories/data/ngs_classification/Updates.xml'
    updates_xml = downloadURL(updates_xml_url, work_dir)

    updates_xml_tree = ET.parse(updates_xml)
    root = updates_xml_tree.getroot()
    for child in root:
        if child.tag == 'PackageUpdate':
            print child.tag
            for child2 in child:
                if child2.tag == 'Name':
                    if child2.text == 'ngs_classification.clark.bacterial_viral_database':
                        do_ngs_classification_clark_bacterial_viral_database(child)
                    elif child2.text == 'ngs_classification.diamond.uniref50_database':
                        do_ngs_classification_diamond_uniref50_database(child)
                    else:
                        print "\t", child2.text
