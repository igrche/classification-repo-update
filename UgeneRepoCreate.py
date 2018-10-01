# coding=utf-8
import logging
import sys
import platform
import tempfile
import os
import shutil
import subprocess


def os_system_cmd(cmd):
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print("EXEC: `" + cmd + "` return {0}".format(err if err else 0))
    return (out, err)


def do_taxonomy(dest_dir_root, list_updated_repo, ext_tools_root):
    taxonomy_dir = list_updated_repo['taxonomy']
    if os.path.isfile(list_updated_repo['taxonomy']):
        taxonomy_dir = os.path.dirname(list_updated_repo['taxonomy'])
    if not os.path.isdir(taxonomy_dir):
        logging.error('taxonomy_dir is not a dir: {0}'.format(taxonomy_dir))
        exit(-1)

    need_to_deal = False
    taxonomy_dest_dir = dest_dir_root + '/ngs_classification.taxonomy/data/data/ngs_classification/taxonomy'

    if not os.path.isdir(taxonomy_dest_dir):
        need_to_deal = True
    elif not os.path.isfile(taxonomy_dest_dir + '/merged.dmp') or \
            not os.path.isfile(taxonomy_dest_dir + '/names.dmp') or \
            not os.path.isfile(taxonomy_dest_dir + '/nodes.dmp'):
        need_to_deal = True
    elif not os.path.isfile(taxonomy_dest_dir + '/nucl_est.accession2taxid') or \
            not os.path.isfile(taxonomy_dest_dir + '/nucl_gb.accession2taxid') or \
            not os.path.isfile(taxonomy_dest_dir + '/nucl_gss.accession2taxid') or \
            not os.path.isfile(taxonomy_dest_dir + '/nucl_wgs.accession2taxid'):
        need_to_deal = True
    elif not os.path.isfile(taxonomy_dest_dir + '/prot.accession2taxid.gz'):
        need_to_deal = True

    if need_to_deal:
        os.chdir(taxonomy_dir)
        if not os.path.isfile(taxonomy_dest_dir + '/merged.dmp') or \
                not os.path.isfile(taxonomy_dest_dir + '/names.dmp') or \
                not os.path.isfile(taxonomy_dest_dir + '/nodes.dmp'):
            (out, err) = os_system_cmd('tar xzf taxdump.tar.gz merged.dmp names.dmp nodes.dmp')

        if not os.path.isfile(taxonomy_dest_dir + '/nucl_est.accession2taxid') or \
                not os.path.isfile(taxonomy_dest_dir + '/nucl_gb.accession2taxid') or \
                not os.path.isfile(taxonomy_dest_dir + '/nucl_gss.accession2taxid') or \
                not os.path.isfile(taxonomy_dest_dir + '/nucl_wgs.accession2taxid'):
            (out, err) = os_system_cmd('gzip -d -k nucl_*.accession2taxid.gz')

        if not os.path.exists(taxonomy_dest_dir):
            os.makedirs(taxonomy_dest_dir)
        if os.path.exists('merged.dmp'):
            shutil.move('merged.dmp', taxonomy_dest_dir + '/merged.dmp')
        if os.path.exists('names.dmp'):
            shutil.move('names.dmp', taxonomy_dest_dir + '/names.dmp')
        if os.path.exists('nodes.dmp'):
            shutil.move('nodes.dmp', taxonomy_dest_dir + '/nodes.dmp')
        if os.path.exists('nucl_est.accession2taxid'):
            shutil.move('nucl_est.accession2taxid', taxonomy_dest_dir + '/nucl_est.accession2taxid')
        if os.path.exists('nucl_gb.accession2taxid'):
            shutil.move('nucl_gb.accession2taxid', taxonomy_dest_dir + '/nucl_gb.accession2taxid')
        if os.path.exists('nucl_gss.accession2taxid'):
            shutil.move('nucl_gss.accession2taxid', taxonomy_dest_dir + '/nucl_gss.accession2taxid')
        if os.path.exists('nucl_wgs.accession2taxid'):
            shutil.move('nucl_wgs.accession2taxid', taxonomy_dest_dir + '/nucl_wgs.accession2taxid')
        if os.path.exists('prot.accession2taxid.gz'):
            shutil.copy('prot.accession2taxid.gz', taxonomy_dest_dir + '/prot.accession2taxid.gz')

    return taxonomy_dest_dir


def do_uniref50(dest_dir_root, list_updated_repo, ext_tools_root):

    if list_updated_repo['uniref50'] or list_updated_repo['taxonomy']:
        diamond = ext_tools_root + os.path.sep + 'diamond-0.9.22' + os.path.sep + 'diamond'

        uniref50_dir = list_updated_repo['uniref50']
        if os.path.isfile(list_updated_repo['uniref50']):
            uniref50_dir = os.path.dirname(list_updated_repo['uniref50'])
        if not os.path.isdir(uniref50_dir):
            logging.error('uniref50_dir is not a dir: {0}'.format(uniref50_dir))
            exit(-1)

        taxonomy_dir = do_taxonomy(dest_dir_root, list_updated_repo, ext_tools_root)

        os.chdir(uniref50_dir)
        cmd = diamond + \
              ' makedb' + \
              ' --in uniref50.fasta.gz' + \
              ' --db uniref50.dmnd' + \
              ' --taxonmap ' + taxonomy_dir + os.path.sep + 'prot.accession2taxid.gz' + \
              ' --taxonnodes ' + taxonomy_dir + os.path.sep + 'nodes.dmp'
        (out, err) = os_system_cmd(cmd)

        uniref_dest_dir = dest_dir_root + '/ngs_classification.diamond.uniref50_database/data/data/ngs_classification/diamond/uniref'
        if not os.path.exists(uniref_dest_dir):
            os.makedirs(uniref_dest_dir)

        shutil.move("uniref50.dmnd", uniref_dest_dir + "/uniref50.dmnd")


def do_uniref90(dest_dir_root, list_updated_repo, ext_tools_root):

    if list_updated_repo['uniref90'] or list_updated_repo['taxonomy']:
        diamond = ext_tools_root + os.path.sep + 'diamond-0.9.22' + os.path.sep + 'diamond'

        uniref90_dir = list_updated_repo['uniref90']
        if os.path.isfile(list_updated_repo['uniref90']):
            uniref90_dir = os.path.dirname(list_updated_repo['uniref90'])
        if not os.path.isdir(uniref90_dir):
            logging.error('uniref90_dir is not a dir: {0}'.format(uniref90_dir))
            exit(-1)

        taxonomy_dir = do_taxonomy(dest_dir_root, list_updated_repo, ext_tools_root)

        os.chdir(uniref90_dir)
        cmd = diamond + \
              ' makedb' + \
              ' --in uniref90.fasta.gz' + \
              ' --db uniref90.dmnd' + \
              ' --taxonmap ' + taxonomy_dir + os.path.sep + 'prot.accession2taxid.gz' + \
              ' --taxonnodes ' + taxonomy_dir + os.path.sep + 'nodes.dmp'
        (out, err) = os_system_cmd(cmd)

        uniref_dest_dir = dest_dir_root + '/ngs_classification.diamond.uniref90_database/data/data/ngs_classification/diamond/uniref'
        if not os.path.exists(uniref_dest_dir):
            os.makedirs(uniref_dest_dir)

        shutil.move("uniref90.dmnd", uniref_dest_dir + "/uniref90.dmnd")


def create_all_repo(dest_dir_root, list_updated_repo, ext_tools_root):
    do_taxonomy(dest_dir_root, list_updated_repo, ext_tools_root)
    do_uniref50(dest_dir_root, list_updated_repo, ext_tools_root)
    do_uniref90(dest_dir_root, list_updated_repo, ext_tools_root)
