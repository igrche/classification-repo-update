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

list_updated_repo = {}

subdirs = {}
subdirs['taxonomy'] = 'ngs_classification.taxonomy/data/data/ngs_classification/taxonomy'
subdirs['uniref50'] = 'ngs_classification.diamond.uniref50_database/data/data/ngs_classification/diamond/uniref'
subdirs['uniref90'] = 'ngs_classification.diamond.uniref90_database/data/data/ngs_classification/diamond/uniref'
subdirs['minikraken_4gb'] = 'ngs_classification.kraken.minikraken_4gb_database/data/data/ngs_classification/kraken/minikraken_4gb'
subdirs['refseq_grch38'] = 'ngs_classification.refseq.grch38/data/data/ngs_classification/refseq/human'
subdirs['refseq_viral'] = 'ngs_classification.refseq.viral/data/data/ngs_classification/refseq/viral'
subdirs['refseq_bacterial'] = 'ngs_classification.refseq.bacterial/data/data/ngs_classification/refseq/bacterial'
subdirs['refseq_viral_database'] = ''
subdirs['refseq_bacterial_database'] = ''

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


def do_ngs_classification_taxonomy(element, dest_dir_root, dest_subdirs):
    if 'taxonomy' in list_updated_repo \
            and list_updated_repo['taxonomy']:
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
        dest_dir_taxonomy = os.path.join(dest_dir_root, dest_subdirs['taxonomy'])
        download_nucl_est_accession2taxid = downloadURL(nucl_est_accession2taxid, dest_dir_taxonomy)
        download_nucl_gb_accession2taxid = downloadURL(nucl_gb_accession2taxid, dest_dir_taxonomy)
        download_nucl_gss_accession2taxid = downloadURL(nucl_gss_accession2taxid, dest_dir_taxonomy)
        download_nucl_wgs_accession2taxid = downloadURL(nucl_wgs_accession2taxid, dest_dir_taxonomy)
        download_prot_accession2taxid = downloadURL(prot_accession2taxid, dest_dir_taxonomy)

        download_taxdump = downloadURL('ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz', dest_dir_taxonomy)

        list_updated_repo['taxonomy'] = download_taxdump
        return True

    return False


def do_ngs_classification_diamond_uniref50_database(element, dest_dir_root, dest_subdirs):
    if 'uniref50' in list_updated_repo \
            and list_updated_repo['uniref50']:
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

    dest_dir_uniref50 = os.path.join(dest_dir_root, dest_subdirs['uniref50'])
    download_uniref50_RELEASE_metalink = downloadURL(remote_uniref50_RELEASE_metalink, dest_dir_uniref50)
    download_uniref50_RELEASE_metalink_tree = ET.parse(download_uniref50_RELEASE_metalink)
    root = download_uniref50_RELEASE_metalink_tree.getroot()

    remote_Version = root.findall('.//{http://www.metalinker.org/}version')[0].text

    ugene_ReleaseDate_array = re.split(r"_|-", ugene_ReleaseDate)
    remote_Version_array = re.split(r"_|-", remote_Version)

    result = False
    if 'ngs_classification.taxonomy' in ugene_Dependencies:
        if do_ngs_classification_taxonomy(element, dest_dir_root, dest_subdirs):
            result = True

    if (ugene_ReleaseDate_array[0] < remote_Version_array[0]):
        result = True
    if (ugene_ReleaseDate_array[1] < remote_Version_array[1]):
        result = True

    if result:
        download_uniref50 = downloadURL(remote_uniref50_fasta_gz, dest_dir_uniref50)
        list_updated_repo['uniref50'] = download_uniref50

    return result


def do_ngs_classification_diamond_uniref90_database(element, dest_dir_root, dest_subdirs):
    if 'uniref90' in list_updated_repo \
            and list_updated_repo['uniref90']:
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

    dest_dir_uniref90 = os.path.join(dest_dir_root, dest_subdirs['uniref90'])
    download_uniref90_RELEASE_metalink = downloadURL(remote_uniref90_RELEASE_metalink, dest_dir_uniref90)
    download_uniref90_RELEASE_metalink_tree = ET.parse(download_uniref90_RELEASE_metalink)
    root = download_uniref90_RELEASE_metalink_tree.getroot()

    remote_Version = root.findall('.//{http://www.metalinker.org/}version')[0].text

    ugene_ReleaseDate_array = re.split(r"_|-", ugene_ReleaseDate)
    remote_Version_array = re.split(r"_|-", remote_Version)

    result = False
    if 'ngs_classification.taxonomy' in ugene_Dependencies:
        if do_ngs_classification_taxonomy(element, dest_dir_root, dest_subdirs):
            result = True

    if (ugene_ReleaseDate_array[0] < remote_Version_array[0]):
        result = True
    if (ugene_ReleaseDate_array[1] < remote_Version_array[1]):
        result = True

    if result:
        download_uniref90 = downloadURL(remote_uniref90_fasta_gz, dest_dir_uniref90)
        list_updated_repo['uniref90'] = True

    return result


def do_ngs_classification_refseq_viral(element, dest_dir_root, dest_subdirs):
    if 'refseq_viral' in list_updated_repo \
            and list_updated_repo['refseq_viral']:
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

    dest_dir_refseq_viral = os.path.join(dest_dir_root, dest_subdirs['refseq_viral'])
    download_refseq_viral_RELEASE_NUMBER = downloadURL(remote_refseq_viral_RELEASE_NUMBER, dest_dir_refseq_viral)
    file = open(download_refseq_viral_RELEASE_NUMBER, "r")
    remote_Version = int(file.read())

    download_refseq_viral = downloadURL(remote_refseq_viral_genomic_fna_gz, dest_dir_refseq_viral, ".genomic.fna.gz")
    list_updated_repo['refseq_viral'] = True

    return True


def do_ngs_classification_refseq_bacterial(element, dest_dir_root, dest_subdirs):
    if 'refseq_bacterial' in list_updated_repo \
            and list_updated_repo['refseq_bacterial']:
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

    dest_dir_refseq_bacterial = os.path.join(dest_dir_root, dest_subdirs['refseq_bacterial'])
    download_refseq_bacterial_RELEASE_NUMBER = downloadURL(remote_refseq_bacterial_RELEASE_NUMBER, dest_dir_refseq_bacterial)
    file = open(download_refseq_bacterial_RELEASE_NUMBER, "r")
    remote_Version = int(file.read())

    download_refseq_bacterial = downloadURL(remote_refseq_bacterial_genomic_fna_gz, dest_dir_refseq_bacterial, ".genomic.fna.gz")
    list_updated_repo['refseq_bacterial'] = True

    return True


def do_ngs_classification_refseq_grch38(element, dest_dir_root, dest_subdirs):
    if 'refseq_grch38' in list_updated_repo \
            and list_updated_repo['refseq_grch38']:
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

    dest_dir_refseq_grch38 = os.path.join(dest_dir_root, dest_subdirs['refseq_grch38'])
    download_refseq_RELEASE_NUMBER = downloadURL(remote_refseq_RELEASE_NUMBER, dest_dir_refseq_grch38)
    file = open(download_refseq_RELEASE_NUMBER, "r")
    remote_Version = int(file.read())

    download_refseq_grch38 = downloadURL(remote_refseq_grch38, dest_dir_refseq_grch38, "CHR_\w+", "hs_ref_GRCh38.p12_chr\w+\.fa\.gz")
    list_updated_repo['refseq_grch38'] = True

    return True


def do_ngs_classification_minikraken_4gb(element, dest_dir_root, dest_subdirs):
    if 'minikraken_4gb' in list_updated_repo \
            and list_updated_repo['minikraken_4gb']:
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
        dest_dir_minikraken_4gb = os.path.join(dest_dir_root, dest_subdirs['minikraken_4gb'])
        download_minikraken_4gb = downloadURL(remote_minikraken_4gb, dest_dir_minikraken_4gb)
        list_updated_repo['minikraken_4gb'] = True

    return True


def download_all(dest_dir_root, ext_tools_root):
    '''
    1) Скачать файл Updates.xml.
    2) Вытащить из него текущие версии нужных компонентов
    '''
    updates_xml_url = 'http://ugene.net/downloads/installer_repositories/data/ngs_classification/Updates.xml'
    updates_xml = downloadURL(updates_xml_url, dest_dir_root)

    updates_xml_tree = ET.parse(updates_xml)
    root = updates_xml_tree.getroot()
    for child in root:
        if child.tag == 'PackageUpdate':
            for child2 in child:
                if child2.tag == 'Name':
                    if child2.text == 'ngs_classification.taxonomy':
                        do_ngs_classification_taxonomy(child, dest_dir_root, subdirs)
                        pass
                    elif child2.text == 'ngs_classification.diamond.uniref50_database':
                        do_ngs_classification_diamond_uniref50_database(child, dest_dir_root, subdirs)
                        pass
                    elif child2.text == 'ngs_classification.diamond.uniref90_database':
                        do_ngs_classification_diamond_uniref90_database(child, dest_dir_root, subdirs)
                        pass
                    elif child2.text == 'ngs_classification.refseq.viral':
                        do_ngs_classification_refseq_viral(child, dest_dir_root, subdirs)
                        pass
                    elif child2.text == 'ngs_classification.refseq.bacterial':
                        do_ngs_classification_refseq_bacterial(child, dest_dir_root, subdirs)
                        pass
                    elif child2.text == 'ngs_classification.refseq.grch38':
                        do_ngs_classification_refseq_grch38(child, dest_dir_root, subdirs)
                        pass
                    elif child2.text == 'ngs_classification.kraken.minikraken_4gb_database':
                        do_ngs_classification_minikraken_4gb(child, dest_dir_root, subdirs)
                        pass
                    else:
                        print "\t", child2.text

    if list_updated_repo['uniref50'] or list_updated_repo['taxonomy']:
        diamond = ext_tools_root + os.path.sep + 'diamond-0.9.22' + os.path.sep + 'diamond'
        os.chdir(list_updated_repo['uniref50'])
        cmd = diamond + \
              ' --in uniref50.fasta.gz' + \
              ' --db uniref50.dmnd' + \
              ' --taxonmap ' + list_updated_repo['taxonomy'] + os.path.sep + 'prot.accession2taxid.gz' + \
              ' --taxonnodes ' + list_updated_repo['taxonomy'] + os.path.sep + 'nodes.dmp}'
        os.system(cmd)

    return list_updated_repo