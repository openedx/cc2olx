import logging
import os.path
import traceback

from cc2olx.settings import collect_settings
from cc2olx import filesystem
from cc2olx import models
from cc2olx.models import Cartridge
from cc2olx import olx


def convert_one_file(settings, input_file):
    print("Converting", input_file)
    workspace = settings['workspace']
    filesystem.create_directory(workspace)
    cartridge = Cartridge(input_file)
    data = cartridge.load_manifest_extracted()
    cartridge.normalize()
    # print()
    # print("=" * 100)
    # import json; print(json.dumps(cartridge.normalized, indent=4))
    xml = olx.OlxExport(cartridge).xml()
    olx_filename = os.path.join(workspace, cartridge.directory + "-course.xml")
    with open(olx_filename, "w") as olxfile:
        olxfile.write(xml)
    tgz_filename = os.path.join(workspace, cartridge.directory + ".tar.gz")
    olx.onefile_tar_gz(tgz_filename, xml.encode("utf8"), "course.xml")


def main():
    settings = collect_settings()
    logging.basicConfig(**settings['logging_config'])
    logger = logging.getLogger()
    for input_file in settings['input_files']:
        try:
            convert_one_file(settings, input_file)
        except Exception:
            traceback.print_exc()


if __name__ == '__main__':
    main()
