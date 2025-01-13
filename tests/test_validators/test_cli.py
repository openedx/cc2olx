import argparse
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError

from cc2olx.validators.cli import convert_to_argparse_validator, link_source_validator


class TestConvertToArgparseValidator:
    def test_original_value_is_return_after_successful_call(self):
        django_validator = Mock()
        argparse_validator = convert_to_argparse_validator(django_validator)
        value_mock = Mock()

        assert argparse_validator(value_mock) == value_mock

    def test_argument_type_error_is_raised_instead_of_intercepted_django_validation_error(self):
        error_message_mock = Mock()
        django_validator = Mock(side_effect=ValidationError(error_message_mock))
        argparse_validator = convert_to_argparse_validator(django_validator)

        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            argparse_validator(Mock())

        assert exc_info.value.args[0] == error_message_mock


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
        ),
    )
    def test_original_value_is_returned_if_it_is_valid(self, links_source: str) -> None:
        """
        Test whether the validator returns original value it is valid.
        """
        assert link_source_validator(links_source) == links_source

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
        ),
    )
    def test_wrong_values_are_detected(self, links_source) -> None:
        """
        Test whether the validator raises an error if the value is invalid.
        """
        with pytest.raises(argparse.ArgumentTypeError, match="Enter a valid URL."):
            link_source_validator(links_source)
