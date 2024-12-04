import argparse

import pytest

from cc2olx.validators.cli import LinkSourceValidator


class TestLinkSourceValidator:
    """
    Test link source validator.
    """

    @pytest.mark.parametrize(
        "links_source",
        (
            "http://example.com",
            "http://example.com/",
            "https://example.com",
            "http://192.168.0.1",
            "http://192.168.0.1:8000/",
            "https://[2001:0db8:85a3::8a2e:0370:7334]/",
        )
    )
    def test_original_value_is_returned_if_it_is_valid(self, links_source: str) -> None:
        """
        Test whether the validator returns original value it is valid.
        """
        assert LinkSourceValidator()(links_source) == links_source

    @pytest.mark.parametrize(
        "links_source",
        (
            "ftp://example.com",
            "ws://example.com",
            "just_string",
            "http://192.168.0.1.9",
            "http://192.168.0.1:-56",
            "http://192.999.0.1",
            "https://m192.168.0.1",
            "https://2001:0db8:85a3::8a2e:0370:7334/",
            "https://[2001:db8:85a3::8a2e:0370:7334::]/",
        )
    )
    def test_wrong_values_are_detected(self, links_source) -> None:
        """
        Test whether the validator raises an error if the value is invalid.
        """
        with pytest.raises(argparse.ArgumentTypeError, match="Enter a valid URL."):
            LinkSourceValidator()(links_source)
