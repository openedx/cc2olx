import logging
import os.path
import pprint

from cc2olx.settings import collect_settings
from cc2olx import filesystem
from cc2olx import models
from cc2olx.models import Cartridge


if __name__ == '__main__':
    settings = collect_settings()
    logging.basicConfig(**settings['logging_config'])
    logger = logging.getLogger()
    workspace = settings['workspace']
    filesystem.create_directory(workspace)
    for input_file in settings['input_files']:
        cartridge = Cartridge(input_file)
        data = cartridge.load_manifest_extracted()
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(data)
        cartridge.serialize()
