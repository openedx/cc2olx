import logging
import os.path
import pprint

from cc2olx.settings import collect_settings
from cc2olx import filesystem
from cc2olx import models


MANIFEST = 'imsmanifest.xml'


if __name__ == '__main__':
    settings = collect_settings()
    logging.basicConfig(**settings['logging_config'])
    logger = logging.getLogger()
    workspace = settings['workspace']
    filesystem.create_directory(workspace)
    for input_file in settings['input_files']:
        path_extracted = filesystem.unzip_directory(input_file, workspace)
        manifest = os.path.join(path_extracted, MANIFEST)
        tree = filesystem.get_xml_tree(manifest)
        root = tree.getroot()
        metadata = models.parse_metadata(root)
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(metadata)
