# coding=utf-8
import logging
import sys
import platform
import tempfile
import os
import xml.etree.ElementTree as ET
import re
import urllib2
from os.path import expanduser
from DownloadAny import downloadURL, get_modify_date

list_downloaded_repo = {}
work_dir = 'classification-repo-update-work'

dest_dir = 'ugene_repo'
dest_dir_taxonomy = 'ngs_classification.taxonomy/data/data/ngs_classification/taxonomy'
dest_dir_uniref50 = 'ngs_classification.diamond.uniref50_database/data/data/ngs_classification/diamond/uniref'
dest_dir_uniref90 = 'ngs_classification.diamond.uniref90_database/data/data/ngs_classification/diamond/uniref'
dest_dir_minikraken_4gb = 'ngs_classification.kraken.minikraken_4gb_database/data/data/ngs_classification/kraken/minikraken_4gb'
dest_dir_refseq_grch38 = 'ngs_classification.refseq.grch38/data/data/ngs_classification/refseq/human'
dest_dir_refseq_viral = 'ngs_classification.refseq.viral/data/data/ngs_classification/refseq/viral'
dest_dir_refseq_bacterial = 'ngs_classification.refseq.bacterial/data/data/ngs_classification/refseq/bacterial'
dest_dir_refseq_viral_database = ''
dest_dir_refseq_bacterial_database = ''

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


def do_ngs_classification_diamond_uniref90_database(element):
    if 'uniref90' in list_downloaded_repo \
            and list_downloaded_repo['uniref90']:
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

    remote_uniref90_RELEASE_metalink = 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref90/RELEASE.metalink'
    remote_uniref90_fasta_gz = 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref90/uniref90.fasta.gz'
    remote_prot_accession2taxid_gz = 'ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.gz'
    remote_prot_accession2taxid_gz_md5 = 'ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.gz.md5'

    work_dir_uniref90 = os.path.join(work_dir, 'uniref90')
    download_uniref90_RELEASE_metalink = downloadURL(remote_uniref90_RELEASE_metalink, work_dir_uniref90)
    download_uniref90_RELEASE_metalink_tree = ET.parse(download_uniref90_RELEASE_metalink)
    root = download_uniref90_RELEASE_metalink_tree.getroot()

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
        download_uniref90 = downloadURL(remote_uniref90_fasta_gz, work_dir_uniref90)
        list_downloaded_repo['uniref90'] = True

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


def do_ngs_classification_refseq_grch38(element):
    if 'refseq_grch38' in list_downloaded_repo \
            and list_downloaded_repo['refseq_grch38']:
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

    remote_refseq_RELEASE_NUMBER = 'ftp://ftp.ncbi.nih.gov/refseq/release/RELEASE_NUMBER'
    remote_refseq_grch38 = 'ftp://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/H_sapiens/'

    work_dir_refseq_grch38 = os.path.join(work_dir, 'refseq_grch38')
    download_refseq_RELEASE_NUMBER = downloadURL(remote_refseq_RELEASE_NUMBER, work_dir_refseq_grch38)
    file = open(download_refseq_RELEASE_NUMBER, "r")
    remote_Version = int(file.read())

    download_refseq_grch38 = downloadURL(remote_refseq_grch38, work_dir_refseq_grch38, "CHR_\w+", "hs_ref_GRCh38.p12_chr\w+\.fa\.gz")
    list_downloaded_repo['refseq_grch38'] = True

    return True


def do_ngs_classification_minikraken_4gb(element):
    if 'minikraken_4gb' in list_downloaded_repo \
            and list_downloaded_repo['minikraken_4gb']:
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

    remote_html_url = 'https://ccb.jhu.edu/software/kraken/'
    remote_response = urllib2.urlopen(remote_html_url)
    remote_html_content = remote_response.read()
    (remote_link, number_of_subs_made) = re.subn(r".+<a href=\"(dl/minikraken_\d\d\d\d\d\d\d\d_4GB.tgz)\">MiniKraken DB_4GB</a>.+",
                                                 r"\1",
                                                 remote_html_content,
                                                 flags=re.DOTALL)
    if number_of_subs_made == 0:
        return None

    (remote_version, number_of_subs_made) = re.subn(r".*dl/minikraken_(\d\d\d\d\d\d\d\d)_4GB.tgz.*",
                                                    r"\1",
                                                    remote_link,
                                                    flags=re.DOTALL)
    if number_of_subs_made == 0:
        return None

    remote_version = remote_version[0:4] + '-' + remote_version[4:6] + '-' + remote_version[6:8]
    remote_minikraken_4gb = remote_html_url + remote_link

    if ugene_ReleaseDate < remote_version:
        work_dir_minikraken_4gb = os.path.join(work_dir, 'minikraken_4gb')
        download_minikraken_4gb = downloadURL(remote_minikraken_4gb, work_dir_minikraken_4gb)
    list_downloaded_repo['minikraken_4gb'] = True

    return True


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
                        pass
                    elif child2.text == 'ngs_classification.diamond.uniref50_database':
                        do_ngs_classification_diamond_uniref50_database(child)
                        pass
                    elif child2.text == 'ngs_classification.diamond.uniref90_database':
                        do_ngs_classification_diamond_uniref90_database(child)
                        pass
                    elif child2.text == 'ngs_classification.refseq.viral':
                        do_ngs_classification_refseq_viral(child)
                        pass
                    elif child2.text == 'ngs_classification.refseq.bacterial':
                        do_ngs_classification_refseq_bacterial(child)
                        pass
                    elif child2.text == 'ngs_classification.refseq.grch38':
                        do_ngs_classification_refseq_grch38(child)
                        pass
                    elif child2.text == 'ngs_classification.kraken.minikraken_4gb_database':
                        do_ngs_classification_minikraken_4gb(child)
                        pass
                    else:
                        print "\t", child2.text

    print 'Downloaded data:\n\t', ('\n\t'.join('{}'.format(item) for item in list_downloaded_repo))