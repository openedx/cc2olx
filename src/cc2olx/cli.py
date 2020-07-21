import argparse

from pathlib import Path

RESULT_TYPE_FOLDER = "folder"
RESULT_TYPE_ZIP = "zip"


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description=(
            "This script converts imscc files into folders with "
            "all the content; in the defined folder structure."
        )
    )
    parser.add_argument(
        "-i",
        "--inputs",
        nargs="*",
        type=lambda p: Path(p).absolute(),
        required=True,
        help=(
            "Please provide the paths to the imscc files or directories "
            "that contain them."
        ),
    )
    parser.add_argument(
        "-l",
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help=(
            "Please provide the appropriate level to change the detail of "
            "logs. It can take one of the following values, DEBUG, INFO, WARNING, "
            "ERROR, CRITICAL as argument."
        ),
    )
    parser.add_argument(
        "-r",
        "--result",
        choices=[RESULT_TYPE_FOLDER, RESULT_TYPE_ZIP],
        default=RESULT_TYPE_FOLDER,
        help=(
            "Please provide the way in which final result "
            "has to be. It can take one of the following "
            "values, {folder}, {zip} as argument.".format(
                folder=RESULT_TYPE_FOLDER, zip=RESULT_TYPE_ZIP
            )
        ),
    )
    return parser.parse_args(args)
