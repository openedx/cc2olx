import re
import xml.dom.minidom
from typing import Dict, List, Optional

from cc2olx import filesystem
from cc2olx.content_processors import AbstractContentProcessor
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.models import ResourceFile
from cc2olx.utils import clean_from_cdata, element_builder


class DiscussionContentProcessor(AbstractContentProcessor):
    """
    Discussion content processor.
    """

    DEFAULT_TEXT = "MISSING CONTENT"

    def process(self, resource: dict, idref: str) -> Optional[List[xml.dom.minidom.Element]]:
        if content := self._parse(resource):
            return self._create_nodes(content)
        return None

    def _parse(self, resource: dict) -> Optional[Dict[str, str]]:
        """
        Parse the resource content.
        """
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

    def _create_nodes(self, content: Dict[str, str]) -> List[xml.dom.minidom.Element]:
        """
        Give out <discussion> and <html> OLX nodes.
        """
        doc = xml.dom.minidom.Document()
        el = element_builder(doc)

        txt = self.DEFAULT_TEXT if content["text"] is None else content["text"]
        txt = clean_from_cdata(txt)
        html_node = el("html", [doc.createCDATASection(txt)], {})

        discussion_node = el(
            "discussion",
            [],
            {
                "display_name": "",
                "discussion_category": content["title"],
                "discussion_target": content["title"],
            },
        )

        return [html_node, discussion_node]
