from enum import Enum


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
