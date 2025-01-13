import argparse

from pathlib import Path

RESULT_TYPE_FOLDER = "folder"
RESULT_TYPE_ZIP = "zip"


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description=(
            "This script converts imscc files into folders with " "all the content; in the defined folder structure."
        )
    )
    parser.add_argument(
        "-i",
        "--inputs",
        nargs="*",
        type=lambda p: Path(p).absolute(),
        required=True,
        help=("Please provide the paths to the imscc files or directories " "that contain them."),
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
            "Please provide the format for output. "
            "It can take one of the following "
            "values, {folder}, {zip} as argument.".format(folder=RESULT_TYPE_FOLDER, zip=RESULT_TYPE_ZIP)
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="output",
        help=("Optionally provide the name for output folder or zipfile (without the .zip extension)."),
    )
    parser.add_argument(
        "-f",
        "--link_file",
        default=None,
        help=(
            "Path for CSV file which has link for videos"
            "and corresponding edx video ID and youtube ID."
            "The header for the file should have External Video Link, Edx Id, Youtube Id"
        ),
    )
    parser.add_argument(
        "-p",
        "--passport-file",
        default=None,
        help=(
            "Path for CSV file which contins the LTI Consumer Id, "
            "LTI Consumer Key and LTI Consumer Secret. The header for the file "
            "should contain consumer_id, consumer_key and consumer_secret."
        ),
    )
    parser.add_argument(
        "-s",
        "--relative_links_source",
        nargs="?",
        help="The relative links source in the format '<scheme>://<netloc>', e.g. 'https://example.com'",
    )
    return parser.parse_args(args)
