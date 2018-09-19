# coding=utf-8
import logging
import sys
import platform
import tempfile
import os
import xml.etree.ElementTree as ET
import re
from os.path import expanduser
from DownloadAny import downloadURL, get_modify_date

work_dir = 'classification-repo-update-work'
list_downloaded_repo = {}

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


def do_ngs_classification_diamond_uniref50_database(element):
    if 'uniref50' in list_downloaded_repo \
            and list_downloaded_repo['uniref50']:
        return True

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
    if 'ngs_classification.taxonomy' in ugene_Dependencies:
        if do_ngs_classification_taxonomy(element):
            result = True

    if (ugene_ReleaseDate_array[0] < remote_Version_array[0]):
        result = True
    if (ugene_ReleaseDate_array[1] < remote_Version_array[1]):
        result = True

    if result:
        download_uniref50 = downloadURL(remote_uniref50_fasta_gz, work_dir_uniref50)
        list_downloaded_repo['uniref50'] = True

    return result


def do_ngs_classification_refseq_viral(element):
    if 'refseq_viral' in list_downloaded_repo \
            and list_downloaded_repo['refseq_viral']:
        return True

    ugene_dict = xml_to_dict(element)
    ugene_Name = ugene_dict['children']['Name']['text']
    ugene_Dependencies = ugene_dict['children']['Dependencies']['text']
    ugene_Version = ugene_dict['children']['Version']['text']
    ugene_ReleaseDate = ugene_dict['children']['ReleaseDate']['text']
    ugene_ReleaseDate = ugene_dict['children']['ReleaseDate']['text']
    ugene_DownloadableArchives = ugene_dict['children']['DownloadableArchives']['text']
    ugene_Script = ugene_dict['children']['Script']['text']
    ugene_OS = ugene_dict['children']['UpdateFile']['attrib']['OS']
    ugene_CompressedSize = ugene_dict['children']['UpdateFile']['attrib']['CompressedSize']
    ugene_UncompressedSize = ugene_dict['children']['UpdateFile']['attrib']['UncompressedSize']
    ugene_SHA1 = ugene_dict['children']['SHA1']['text']

    remote_refseq_viral_RELEASE_NUMBER = 'ftp://ftp.ncbi.nih.gov/refseq/release/RELEASE_NUMBER'
    remote_refseq_viral_genomic_fna_gz = 'ftp://ftp.ncbi.nlm.nih.gov/refseq/release/viral/'

    work_dir_refseq_viral = os.path.join(work_dir, 'refseq_viral')
    download_refseq_viral_RELEASE_NUMBER = downloadURL(remote_refseq_viral_RELEASE_NUMBER, work_dir_refseq_viral)
    file = open(download_refseq_viral_RELEASE_NUMBER, "r")
    remote_Version = int(file.read())

    download_refseq_viral = downloadURL(remote_refseq_viral_genomic_fna_gz, work_dir_refseq_viral, ".genomic.fna.gz")
    list_downloaded_repo['refseq_viral'] = True

    return True


def do_ngs_classification_refseq_bacterial(element):
    if 'refseq_bacterial' in list_downloaded_repo \
            and list_downloaded_repo['refseq_bacterial']:
        return True

    ugene_dict = xml_to_dict(element)
    ugene_Name = ugene_dict['children']['Name']['text']
    ugene_Dependencies = ugene_dict['children']['Dependencies']['text']
    ugene_Version = ugene_dict['children']['Version']['text']
    ugene_ReleaseDate = ugene_dict['children']['ReleaseDate']['text']
    ugene_ReleaseDate = ugene_dict['children']['ReleaseDate']['text']
    ugene_DownloadableArchives = ugene_dict['children']['DownloadableArchives']['text']
    ugene_Script = ugene_dict['children']['Script']['text']
    ugene_OS = ugene_dict['children']['UpdateFile']['attrib']['OS']
    ugene_CompressedSize = ugene_dict['children']['UpdateFile']['attrib']['CompressedSize']
    ugene_UncompressedSize = ugene_dict['children']['UpdateFile']['attrib']['UncompressedSize']
    ugene_SHA1 = ugene_dict['children']['SHA1']['text']

    remote_refseq_bacterial_RELEASE_NUMBER = 'ftp://ftp.ncbi.nih.gov/refseq/release/RELEASE_NUMBER'
    remote_refseq_bacterial_genomic_fna_gz = 'ftp://ftp.ncbi.nlm.nih.gov/refseq/release/bacteria/'

    work_dir_refseq_bacterial = os.path.join(work_dir, 'refseq_bacterial')
    download_refseq_bacterial_RELEASE_NUMBER = downloadURL(remote_refseq_bacterial_RELEASE_NUMBER, work_dir_refseq_bacterial)
    file = open(download_refseq_bacterial_RELEASE_NUMBER, "r")
    remote_Version = int(file.read())

    download_refseq_bacterial = downloadURL(remote_refseq_bacterial_genomic_fna_gz, work_dir_refseq_bacterial, ".genomic.fna.gz")
    list_downloaded_repo['refseq_bacterial'] = True

    return True


def do_ngs_classification_taxonomy(element):
    if 'taxonomy' in list_downloaded_repo \
            and list_downloaded_repo['taxonomy']:
        return True

    ugene_dict = xml_to_dict(element)
    ugene_ReleaseDate = ugene_dict['children']['ReleaseDate']['text']

    remote_taxonomy_cwd = 'ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/'

    nucl_est_accession2taxid = remote_taxonomy_cwd + 'nucl_est.accession2taxid.gz'
    nucl_gb_accession2taxid  = remote_taxonomy_cwd + 'nucl_gb.accession2taxid.gz'
    nucl_gss_accession2taxid = remote_taxonomy_cwd + 'nucl_gss.accession2taxid.gz'
    nucl_wgs_accession2taxid = remote_taxonomy_cwd + 'nucl_wgs.accession2taxid.gz'
    prot_accession2taxid     = remote_taxonomy_cwd + 'prot.accession2taxid.gz'

    remote_modify_date = get_modify_date(prot_accession2taxid)
    if ugene_ReleaseDate < remote_modify_date:
        work_dir_taxonomy = os.path.join(work_dir, 'taxonomy')
        download_nucl_est_accession2taxid = downloadURL(nucl_est_accession2taxid, work_dir_taxonomy)
        download_nucl_gb_accession2taxid = downloadURL(nucl_gb_accession2taxid, work_dir_taxonomy)
        download_nucl_gss_accession2taxid = downloadURL(nucl_gss_accession2taxid, work_dir_taxonomy)
        download_nucl_wgs_accession2taxid = downloadURL(nucl_wgs_accession2taxid, work_dir_taxonomy)
        download_prot_accession2taxid = downloadURL(prot_accession2taxid, work_dir_taxonomy)

        download_taxdump = downloadURL('ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz', work_dir_taxonomy)

        list_downloaded_repo['taxonomy'] = True
        return True

    return False



if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    home_dir = expanduser("~")

    if platform.system() == "Windows":
        work_dir = "e:\\ichebyki\\Downloads\\" + work_dir
    else:
        work_dir = "/home/ichebyki/Downloads/" + work_dir

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
            for child2 in child:
                if child2.tag == 'Name':
                    if child2.text == 'ngs_classification.taxonomy':
                        do_ngs_classification_taxonomy(child)
                    elif child2.text == 'ngs_classification.diamond.uniref50_database':
                        do_ngs_classification_diamond_uniref50_database(child)
                    elif child2.text == 'ngs_classification.refseq.viral':
                        do_ngs_classification_refseq_viral(child)
                    elif child2.text == 'ngs_classification.refseq.bacterial':
                        do_ngs_classification_refseq_bacterial(child)
                    else:
                        print "\t", child2.text

    print 'Downloaded data:\n\t', ('\n\t'.join('{}'.format(item) for item in list_downloaded_repo))