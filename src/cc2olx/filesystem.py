import logging
import tarfile
import zipfile

from xml.etree import ElementTree

logger = logging.getLogger()


def create_directory(directory_path):
    if not directory_path.exists():
        directory_path.mkdir()
        logger.debug("Created the folder: %s", directory_path)


def get_xml_tree(path_src):
    logger.info('Loading file %s', path_src)
    try:
        tree = ElementTree.parse(str(path_src))
        return tree
    except ElementTree.ParseError:
        logger.error(
            "Error while reading xml from %s.", path_src, exc_info=True
        )


def unzip_directory(path_src, path_dst_base=None):
    src_dir_path = path_src.parent
    path_dst_base = path_dst_base or src_dir_path

    path_dst = path_dst_base / path_src.stem

    with zipfile.ZipFile(str(path_src)) as output_file:
        output_file.extractall(str(path_dst))

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
    with tarfile.open(archive_name, 'w:gz') as archive:
        for file, alternative_name in inputs:
            # Disregard any file that isn't found
            try:
                archive.add(file, alternative_name)
            except FileNotFoundError:
                logger.error(
                    "%s was not found. Skipping", str(file), exc_info=True
                )

    return archive_name
