from enum import Enum
from typing import Set


class CommonCartridgeResourceType(str, Enum):
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


class SupportedCustomBlockContentType(str, Enum):
    """
    Enumerate supported custom block content types.

    A xBlock is considered as the custom one if it is not built in Open edX by
    default.
    """

    PDF = "pdf"

    @property
    def file_extensions(self) -> Set[str]:
        """
        Provide file extensions the block content type supports.
        """
        return {
            SupportedCustomBlockContentType.PDF: {".pdf"},
        }[self]
