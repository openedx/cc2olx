from enum import StrEnum
from typing import Set


class CommonCartridgeResourceType(StrEnum):
    """
    Enumerate Common Cartridge resource types.

    Contain the exact type values and regular expressions to match the type.
    """

    WEB_CONTENT = "webcontent"
    WEB_LINK = r"^imswl_xmlv\d+p\d+$"
    LTI_LINK = r"^imsbasiclti_xmlv\d+p\d+$"
    QTI_ASSESSMENT = r"^imsqti_xmlv\d+p\d+/imscc_xmlv\d+p\d+/assessment$"
    DISCUSSION_TOPIC = r"^imsdt_xmlv\d+p\d+$"
    ASSIGNMENT = r"^assignment_xmlv\d+p\d+$"


class SupportedCustomBlockContentType(StrEnum):
    """
    Enumerate supported custom block content types.

    An XBlock is considered "custom" if it is not distributed with Open edX by
    default.
    """

    PDF = "pdf"

    @property
    def file_extensions(self) -> Set[str]:
        """
        Provide file extensions the block content type supports.
        """
        return {
            self.PDF: {".pdf"},
        }[self]
