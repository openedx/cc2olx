import logging
import os.path

from cc2olx.settings import collect_settings
from cc2olx import filesystem


MANIFEST = 'imsmanifest.xml'


if __name__ == '__main__':
    settings = collect_settings()
    logging.basicConfig(**settings['logging_config'])
    logger = logging.getLogger()
    workspace = settings['workspace']
    filesystem.create_directory(workspace)
    for input_file in settings['input_files']:
        logger.info("Processing file: %s", input_file)
        path_extracted = filesystem.unzip_directory(input_file, workspace)
        manifest = os.path.join(path_extracted, MANIFEST)
        tree = filesystem.get_xml_tree(manifest)
        root = tree.getroot()
