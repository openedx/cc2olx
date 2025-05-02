import argparse
from pathlib import Path

from cc2olx.enums import SupportedCustomBlockContentType
from cc2olx.logging import build_console_logger
from cc2olx.validators.cli import link_source_validator

RESULT_TYPE_FOLDER = "folder"
RESULT_TYPE_ZIP = "zip"

console_logger = build_console_logger(__name__)


class AppendIfAllowedAction(argparse._AppendAction):
    """
    Store a list and append only allowed argument values to the list.
    """

    NOT_ALLOWED_CHOICE_MESSAGE = (
        "The choice {choice_name!r} is not allowed for {argument_name} argument. It will be ignored during processing."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._choices = self.choices
        self.choices = None

    def __call__(self, parser, namespace, values, option_string=None):
        if values in self._choices:
            super().__call__(parser, namespace, values, option_string)
        else:
            argument_name = "/".join(self.option_strings)
            console_logger.warning(
                self.NOT_ALLOWED_CHOICE_MESSAGE.format(choice_name=values, argument_name=argument_name)
            )


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description=(
            "This script converts imscc files into folders with all the content; in the defined folder structure."
        )
    )
    parser.add_argument(
        "-i",
        "--inputs",
        action="append",
        type=lambda p: Path(p).absolute(),
        required=True,
        help="Please provide the paths to the imscc files or directories that contain them.",
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
        type=link_source_validator,
        help="The relative links source in the format '<scheme>://<netloc>', e.g. 'https://example.com'",
    )
    parser.add_argument(
        "-c",
        "--content_types_with_custom_blocks",
        action=AppendIfAllowedAction,
        default=[],
        choices=list(SupportedCustomBlockContentType),
        help="Names of content types for which custom xblocks will be used.",
    )
    parser.add_argument(
        "--logs_dir",
        nargs="?",
        type=str,
        help=(
            "The directory where to store the input file converting logs. If the parameter is not specified, "
            "log files won't be created."
        ),
    )
    return parser.parse_args(args)
