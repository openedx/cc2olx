import sys
import traceback

from cc2olx import filesystem
from cc2olx import olx
from cc2olx.cli import parse_args
from cc2olx.models import Cartridge
from cc2olx.settings import collect_settings


def convert_one_file(settings, input_file):
    workspace = settings['workspace']
    filesystem.create_directory(workspace)

    cartridge = Cartridge(input_file, settings)
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    xml = olx.OlxExport(cartridge).xml()
    olx_filename = cartridge.directory.parent / (
        cartridge.directory.name + "-course.xml"
    )

    with open(olx_filename, "w") as olxfile:
        olxfile.write(xml)

    tgz_filename = cartridge.directory.parent / (
        cartridge.directory.name + ".tar.gz"
    )
    olx.onefile_tar_gz(tgz_filename, xml.encode("utf8"), "course.xml")


def main():
    parsed_args = parse_args()
    settings = collect_settings(parsed_args)

    for input_file in settings['input_files']:
        try:
            convert_one_file(settings, input_file)
        except Exception:
            traceback.print_exc()

    return 0


if __name__ == "__main__":
    sys.exit(main())
