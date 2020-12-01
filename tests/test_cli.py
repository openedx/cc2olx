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
    )
