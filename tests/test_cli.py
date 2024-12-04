from argparse import Namespace

from cc2olx.cli import parse_args


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
    )
