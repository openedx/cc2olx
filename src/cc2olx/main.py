import shutil
import sys
import tempfile
import traceback

from pathlib import Path

from cc2olx import filesystem
from cc2olx import olx
from cc2olx.cli import parse_args, RESULT_TYPE_FOLDER, RESULT_TYPE_ZIP
from cc2olx.models import Cartridge
from cc2olx.settings import collect_settings


def convert_one_file(input_file, workspace):
    filesystem.create_directory(workspace)

    cartridge = Cartridge(input_file, workspace)
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    xml = olx.OlxExport(cartridge).xml()
    olx_filename = cartridge.directory.parent / (
        cartridge.directory.name + "-course.xml"
    )

    with open(str(olx_filename), "w") as olxfile:
        olxfile.write(xml)

    tgz_filename = (workspace / cartridge.directory.name).with_suffix('.tar.gz')

    filesystem.add_in_tar_gz(str(tgz_filename), [
        (str(olx_filename), 'course.xml'),
        (str(cartridge.directory / 'web_resources'), '/static/')
    ])


def main():
    parsed_args = parse_args()
    settings = collect_settings(parsed_args)

    workspace = settings["workspace"]

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_workspace = Path(tmpdirname) / workspace.stem

        for input_file in settings["input_files"]:
            try:
                convert_one_file(input_file, temp_workspace)
            except Exception:
                traceback.print_exc()

        if settings["output_format"] == RESULT_TYPE_FOLDER:
            shutil.rmtree(str(workspace), ignore_errors=True)
            shutil.copytree(str(temp_workspace), str(workspace))

        if settings["output_format"] == RESULT_TYPE_ZIP:
            shutil.make_archive(str(workspace), "zip", str(temp_workspace))

    return 0


if __name__ == "__main__":
    sys.exit(main())
