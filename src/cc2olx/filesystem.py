import logging
import tarfile
import zipfile

from xml.etree import ElementTree

from cc2olx.utils import clean_file_name
from cc2olx.xml.cc_xml import CommonCartridgeXmlParser

logger = logging.getLogger()


def create_directory(directory_path):
    if not directory_path.exists():
        directory_path.mkdir()
        logger.debug("Created the folder: %s", directory_path)


def get_xml_tree(path_src):
    """
    This is one of the core funtions, it helps parse a given xml file and
    return an xml tree object.

    Args:
        path_src ([str]): File path that needs to be parsed.

    Returns:
        ElementTree: This gives back an xml parse tree that can handle different operation
    """
    logger.info("Loading file %s", path_src)
    try:
        # We are using this parser with recover and encoding options so that we are
        # able to parse malformed xml without much issue. The xml that we are
        # anticipating can even be having certain non-acceptable characters like &nbsp.
        parser = CommonCartridgeXmlParser(encoding="utf-8", recover=True, ns_clean=True)
        tree = ElementTree.parse(str(path_src), parser=parser)
        return tree
    except ElementTree.ParseError:
        logger.error("Error while reading xml from %s.", path_src, exc_info=True)


def unzip_directory(path_src, path_dst_base=None):
    src_dir_path = path_src.parent
    path_dst_base = path_dst_base or src_dir_path

    path_dst = path_dst_base / path_src.stem

    output_file = zipfile.ZipFile(str(path_src))
    zip_list = output_file.infolist()

    for zip in zip_list:
        zip.filename = clean_file_name(zip.filename)
        output_file.extract(zip, path=str(path_dst))

    return path_dst


def add_in_tar_gz(archive_name, inputs):
    """
    Creates ``.tar.gz`` archive using given list of files.

    Args:
        archive_name: path to resulting archive with name.
        inputs: list of tuples like ``('assets', 'static')``,
            where first element is any type of file, and second is
            an alternative name of file in archive.

    Returns: path to the newly created archive.
    """
    with tarfile.open(archive_name, "w:gz") as archive:
        for file, alternative_name in inputs:
            # Disregard any file that isn't found
            try:
                archive.add(file, alternative_name)
            except FileNotFoundError:
                logger.error("%s was not found. Skipping", str(file))

    return archive_name
