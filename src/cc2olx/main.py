import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

import django
from django.conf import settings

from cc2olx import filesystem, olx
from cc2olx.cli import parse_args, RESULT_TYPE_FOLDER, RESULT_TYPE_ZIP
from cc2olx.constants import OLX_STATIC_DIR
from cc2olx.models import Cartridge
from cc2olx.parser import parse_options


def convert_one_file(
    input_file,
    workspace,
    link_file=None,
    passport_file=None,
    relative_links_source=None,
    content_types_with_custom_blocks=None,
):
    content_types_with_custom_blocks = content_types_with_custom_blocks or []

    filesystem.create_directory(workspace)

    cartridge = Cartridge(input_file, workspace)
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    olx_export = olx.OlxExport(
        cartridge,
        link_file,
        passport_file,
        relative_links_source,
        content_types_with_custom_blocks,
    )
    olx_filename = cartridge.directory.parent / (cartridge.directory.name + "-course.xml")
    policy_filename = cartridge.directory.parent / "policy.json"

    with open(str(olx_filename), "w", encoding="utf-8") as olxfile:
        olxfile.write(olx_export.xml())

    with open(str(policy_filename), "w", encoding="utf-8") as policy:
        policy.write(olx_export.policy())

    tgz_filename = (workspace / cartridge.directory.name).with_suffix(".tar.gz")

    file_list = [
        (str(olx_filename), "course.xml"),
        (str(policy_filename), "policies/course/policy.json"),
        (str(cartridge.directory / "web_resources"), "/{}/".format(OLX_STATIC_DIR)),
    ]

    # Add static files that are outside of web_resources directory
    file_list += [
        (str(cartridge.directory / original_filepath), olx_static_path)
        for olx_static_path, original_filepath in cartridge.olx_to_original_static_file_paths.extra.items()
    ]

    filesystem.add_in_tar_gz(str(tgz_filename), file_list)


def main():
    initialize_django()

    args = parse_args()
    options = parse_options(args)

    workspace = options["workspace"]
    link_file = options["link_file"]
    passport_file = options["passport_file"]
    relative_links_source = options["relative_links_source"]
    content_types_with_custom_blocks = options["content_types_with_custom_blocks"]

    # setup logger
    logging.basicConfig(level=options["log_level"], format=settings.LOG_FORMAT)
    logger = logging.getLogger()

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_workspace = Path(tmpdirname) / workspace.stem

        for input_file in options["input_files"]:
            try:
                convert_one_file(
                    input_file,
                    temp_workspace,
                    link_file,
                    passport_file,
                    relative_links_source,
                    content_types_with_custom_blocks,
                )
            except Exception:
                logger.exception("Error while converting %s file", input_file)

        if options["output_format"] == RESULT_TYPE_FOLDER:
            shutil.rmtree(str(workspace), ignore_errors=True)
            shutil.copytree(str(temp_workspace), str(workspace))

        if options["output_format"] == RESULT_TYPE_ZIP:
            shutil.make_archive(str(workspace), "zip", str(temp_workspace))

    logger.info("Conversion completed")

    return 0


def initialize_django():
    """
    Initialize the Django package.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cc2olx.settings")
    django.setup()


if __name__ == "__main__":
    sys.exit(main())
