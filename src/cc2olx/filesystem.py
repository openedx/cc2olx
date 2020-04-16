import logging
import os
import shutil
import zipfile

from xml.etree import ElementTree

logger = logging.getLogger()


def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.debug(
            "Created the folder: %s",
            directory_path,
        )


def get_xml_tree(path_src):
    xml_data = ''
    try:
        tree = ElementTree.parse(path_src)
    except Exception as e:
        logger.error("Error while reading xml from %s.", path_src, exc_info=True)
    return tree


def strip_extension(input_path):
    input_dir, input_file = os.path.split(input_path)
    input_file_name = os.path.splitext(input_file)[0]
    return input_file_name


def unzip_directory(path_src, path_dst_base=None):
    src_dir_path = os.path.dirname(path_src)
    file_name_without_extension = strip_extension(path_src)
    if not path_dst_base:
        path_dst_base = os.path.join(src_dir_path, file_name_without_extension)
    path_dst = os.path.join(path_dst_base, file_name_without_extension)
    with zipfile.ZipFile(path_src) as output_file:
        output_file.extractall(path_dst)
    return path_dst
