import re
from typing import Dict, Optional

from cc2olx import filesystem
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.models import Cartridge


class WebLinkParserMixin:
    """
    Provide Common Cartridge Web Link resource parsing functionality.
    """

    _cartridge: Cartridge

    def _parse_web_link_content(self, resource: dict) -> Optional[Dict[str, str]]:
        """
        Provide Web Link resource data.
        """
        resource_type = resource["type"]
        if re.match(CommonCartridgeResourceType.WEB_LINK, resource_type):
            resource_file = resource["children"][0]
            resource_file_path = self._cartridge.build_resource_file_path(resource_file.href)
            tree = filesystem.get_xml_tree(resource_file_path)
            root = tree.getroot()
            return {
                "href": root.get_url(resource_type).get("href"),
                "text": root.get_title(resource_type).text,
            }
        return None
