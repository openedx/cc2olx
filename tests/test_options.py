from pathlib import Path

from cc2olx.cli import parse_args
from cc2olx.parser import parse_options


def test_parse_options(imscc_file):
    parsed_args = parse_args(["-i", str(imscc_file)])

    options = parse_options(parsed_args)

    assert options == {
        "input_files": {imscc_file},
        "output_format": parsed_args.result,
        "workspace": Path.cwd() / "output",
        "link_file": None,
        "passport_file": None,
        "log_level": parsed_args.loglevel,
        "relative_links_source": None,
    }
