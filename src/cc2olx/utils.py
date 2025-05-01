"""
Utility functions for cc2olx.
"""

import csv
import re
import string
import xml.dom.minidom
from typing import Generator

from cc2olx.logging import build_console_logger

CDATA_PATTERN = r"<!\[CDATA\[(?P<content>.*?)\]\]>"

console_logger = build_console_logger(__name__)


def element_builder(xml_doc):
    """
    Given a document returns a function to build xml elements.

    Args:
        xml_doc (xml.dom.minidom.Document)

    Returns:
        element (func)
    """

    def element(name, children, attributes=None):
        """
        An utility to help build xml tree in a managable way.

        Args:
            name (str) - tag name
            children (str|list|xml.dom.minidom.Element)
            attributes (dict)

        Returns:
            elem (xml.dom.minidom.Element)
        """

        elem = xml_doc.createElement(name)

        # set attributes if exists
        if attributes is not None and isinstance(attributes, dict):
            [elem.setAttribute(key, val) for key, val in attributes.items()]

        # set children if exists
        if children is not None:
            if isinstance(children, list) or isinstance(children, tuple):
                [elem.appendChild(c) for c in children]
            elif isinstance(children, str):
                elem.appendChild(xml_doc.createTextNode(children))
            else:
                elem.appendChild(children)

        return elem

    return element


def simple_slug(value: str):
    char_to_convert = string.punctuation + " "
    slug = "".join(char if char not in char_to_convert else "_" for char in value)
    return slug.replace("__", "_").strip("_").lower()


def passport_file_parser(filename: str):
    """
    Reads and parse passport file.

    Args:
        filename (str) - path of the file containing lti consumer details

    Returns:
        passports (dict) - Dictionary with lti consumer id and corresponding passports
    """
    required_fields = ["consumer_id", "consumer_key", "consumer_secret"]
    with open(filename, "r", encoding="utf-8") as csvfile:
        passport_file = csv.DictReader(csvfile)

        # Validation: File should contain the required headers.
        headers = passport_file.fieldnames or []
        fields_in_header = [field in headers for field in required_fields]
        if not all(fields_in_header):
            console_logger.warning(
                "Ignoring passport file (%s). Please ensure that the file"
                " contains required headers consumer_id, consumer_key and consumer_secret.",
                filename,
            )
            return {}

        passports = dict()
        for row in passport_file:
            passport = "{lti_id}:{key}:{secret}".format(
                lti_id=row["consumer_id"], key=row["consumer_key"], secret=row["consumer_secret"]
            )
            passports[row["consumer_id"]] = passport

        return passports


def clean_file_name(filename: str):
    """
    Replaces any reserved characters with an underscore so the filename can be used in read and write
    operations

    Args:
        filename (str) - path of the file to be cleaned

    Returns:
        filename (str) - filename with the reserved characters removed
    """
    special_characters = r"[\?\*\|:><]"

    cleaned_name = re.sub(special_characters, "_", filename)
    return cleaned_name


def clean_from_cdata(xml_string: str) -> str:
    """
    Deletes CDATA tag from XML string while keeping its content.

    Args:
        xml_string (str): original XML string to clean.

    Returns:
        str: cleaned XML string.
    """
    return re.sub(CDATA_PATTERN, r"\g<content>", xml_string, flags=re.DOTALL)


def get_xml_minidom_element_iterator(
    element: xml.dom.minidom.Element,
) -> Generator[xml.dom.minidom.Element, None, None]:
    """
    Provide an iterator over XML minidom Element hierarchy.
    """
    yield element

    for child in element.childNodes:
        yield from get_xml_minidom_element_iterator(child)


def build_default_exception_output(exception: Exception) -> str:
    """
    Build the default exception output.
    """
    return f"{type(exception).__name__}: {exception}"
