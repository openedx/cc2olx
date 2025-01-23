import re
from typing import Dict, Optional

from cc2olx import filesystem
from cc2olx.content_parsers import AbstractContentParser
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.models import ResourceFile


class DiscussionContentParser(AbstractContentParser):
    """
    Discussion resource content parser.
    """

    def _parse_content(self, idref: Optional[str]) -> Optional[Dict[str, str]]:
        if idref:
            if resource := self._cartridge.define_resource(idref):
                if re.match(CommonCartridgeResourceType.DISCUSSION_TOPIC, resource["type"]):
                    return self._parse_discussion(resource)
        return None

    def _parse_discussion(self, resource: dict) -> Dict[str, str]:
        """
        Parse the discussion content.
        """
        data = {}

        for child in resource["children"]:
            if isinstance(child, ResourceFile):
                data.update(self._parse_resource_file_data(child, resource["type"]))

        return data

    def _parse_resource_file_data(self, resource_file: ResourceFile, resource_type: str) -> Dict[str, str]:
        """
        Parse the discussion resource file.
        """
        tree = filesystem.get_xml_tree(self._cartridge.build_resource_file_path(resource_file.href))
        root = tree.getroot()

        return {
            "title": root.get_title(resource_type).text,
            "text": root.get_text(resource_type).text,
        }
