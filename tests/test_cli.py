from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cc2olx.cli import parse_args
from .utils import build_multi_value_args


def test_parse_args(imscc_file):
    """
    Basic cli test.
    """

    parsed_args = parse_args(
        [
            "-i",
            str(imscc_file),
        ]
    )

    assert parsed_args == Namespace(
        inputs=[imscc_file],
        loglevel="INFO",
        result="folder",
        link_file=None,
        passport_file=None,
        output="output",
        relative_links_source=None,
        content_types_with_custom_blocks=[],
    )


def test_parse_args_csv_file(imscc_file, link_map_csv):
    """
    Basic cli test with csv file parsed.
    """

    parsed_args = parse_args(["-i", str(imscc_file), "-f", link_map_csv])

    assert parsed_args == Namespace(
        inputs=[imscc_file],
        loglevel="INFO",
        result="folder",
        link_file=link_map_csv,
        passport_file=None,
        output="output",
        relative_links_source=None,
        content_types_with_custom_blocks=[],
    )


def test_parse_args_passport_file(imscc_file, passports_csv):
    """
    Input test for lti passport csv
    """
    parsed_args = parse_args(["-i", str(imscc_file), "-p", passports_csv])
    assert parsed_args == Namespace(
        inputs=[imscc_file],
        loglevel="INFO",
        result="folder",
        link_file=None,
        passport_file=passports_csv,
        output="output",
        relative_links_source=None,
        content_types_with_custom_blocks=[],
    )


def test_parse_args_with_correct_relative_links_source(imscc_file: Path) -> None:
    """
    Positive input test for relative links source argument.
    """
    relative_links_source = "https://example.com"

    parsed_args = parse_args(["-i", str(imscc_file), "-s", relative_links_source])

    assert parsed_args == Namespace(
        inputs=[imscc_file],
        loglevel="INFO",
        result="folder",
        link_file=None,
        passport_file=None,
        output="output",
        relative_links_source=relative_links_source,
        content_types_with_custom_blocks=[],
    )


def test_parse_args_with_incorrect_relative_links_source(imscc_file: Path) -> None:
    """
    Test arguments parser detects incorrect relative links sources.
    """
    relative_links_source = "ws://example.com"

    with pytest.raises(SystemExit):
        parse_args(["-i", str(imscc_file), "-s", relative_links_source])


def test_parse_args_with_correct_content_types_with_custom_blocks(imscc_file: Path) -> None:
    """
    Positive input test for content types with custom blocks argument.
    """
    content_types_with_custom_blocks = ["pdf"]
    content_types_with_custom_blocks_args = build_multi_value_args("-c", content_types_with_custom_blocks)

    parsed_args = parse_args(["-i", str(imscc_file), *content_types_with_custom_blocks_args])

    assert parsed_args == Namespace(
        inputs=[imscc_file],
        loglevel="INFO",
        result="folder",
        link_file=None,
        passport_file=None,
        output="output",
        relative_links_source=None,
        content_types_with_custom_blocks=content_types_with_custom_blocks,
    )


@pytest.mark.parametrize(
    "content_type_with_custom_block",
    ["word_document", "poll", "survey", "feedback", "image", "audio", "llm"],
)
@patch("cc2olx.cli.logger")
def test_parse_args_with_incorrect_content_types_with_custom_blocks(
    logger_mock: MagicMock,
    imscc_file: Path,
    content_type_with_custom_block: str,
) -> None:
    """
    Test arguments parser logs incorrect content types with custom blocks.
    """
    expected_log_message = (
        f"The choice '{content_type_with_custom_block}' is not allowed for -c/--content_types_with_custom_blocks "
        f"argument. It will be ignored during processing."
    )

    parse_args(["-i", str(imscc_file), "-c", content_type_with_custom_block])

    logger_mock.warning.assert_called_once_with(expected_log_message)
