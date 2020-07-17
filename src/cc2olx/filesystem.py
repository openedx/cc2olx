import logging
import zipfile

from xml.etree import ElementTree

logger = logging.getLogger()


def create_directory(directory_path):
    if not directory_path.exists():
        directory_path.mkdir()
        logger.debug("Created the folder: %s", directory_path)


def get_xml_tree(path_src):
    xml_data = ''
    try:
        tree = ElementTree.parse(path_src)
    except Exception as e:
        logger.error("Error while reading xml from %s.", path_src, exc_info=True)
    return tree


def unzip_directory(path_src, path_dst_base=None):
    src_dir_path = path_src.parent
    path_dst_base = path_dst_base or src_dir_path

    path_dst = path_dst_base / path_src.stem

    with zipfile.ZipFile(path_src) as output_file:
        output_file.extractall(path_dst)

    return path_dst
