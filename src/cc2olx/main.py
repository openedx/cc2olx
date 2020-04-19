import logging
import os.path
import pprint

from cc2olx.settings import collect_settings
from cc2olx import filesystem
from cc2olx import models
from cc2olx.models import Cartridge
from cc2olx import olx


if __name__ == '__main__':
    settings = collect_settings()
    logging.basicConfig(**settings['logging_config'])
    logger = logging.getLogger()
    workspace = settings['workspace']
    filesystem.create_directory(workspace)
    for input_file in settings['input_files']:
        cartridge = Cartridge(input_file)
        data = cartridge.load_manifest_extracted()
        pp = pprint.PrettyPrinter(indent=2, width=160)
        cartridge.normalize()
        cartridge.serialize()
        print()
        print("=" * 100)
        import json; print(json.dumps(cartridge.normalized, indent=4))
        xml = olx.OlxExport(cartridge).xml()
        print(xml)
        print("=" * 60)
        pp.pprint(cartridge.resources_by_id)
        tgz_filename = os.path.join(workspace, cartridge.directory + "-onefile.tar.gz")
        olx.onefile_tar_gz(tgz_filename, xml.encode("utf8"), "course.xml")
