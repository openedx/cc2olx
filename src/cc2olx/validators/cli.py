import argparse
import re
from typing import Callable

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def convert_to_argparse_validator(django_validator: Callable) -> Callable:
    """
    Convert a Django validator to an argparse validator.

    If a Django ValidationError is raised during the validator call, it is
    intercepted and an ArgumentTypeError is raised with the same message.
    """

    def argparse_validator(value):
        try:
            django_validator(value)
        except ValidationError as exc:
            raise argparse.ArgumentTypeError(exc.message) from exc
        return value

    return argparse_validator


link_source_validator = convert_to_argparse_validator(
    URLValidator(
        schemes=["http", "https"],
        regex=(
            r"^(?:[a-z0-9.+-]*)://"  # scheme is validated separately
            r"(?:[^\s:@/]+(?::[^\s:@/]*)?@)?"  # user:pass authentication
            r"(?:" + URLValidator.ipv4_re + "|" + URLValidator.ipv6_re + "|" + URLValidator.host_re + ")"
            r"(?::[0-9]{1,5})?"  # port
            r"/?"  # trailing slash
            r"\Z"
        ),
        flags=re.IGNORECASE,
    )
)
