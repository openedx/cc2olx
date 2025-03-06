import re
import xml.dom.minidom
from typing import Dict, List, Optional

from cc2olx import filesystem
from cc2olx.content_processors import AbstractContentProcessor
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.utils import element_builder, simple_slug
from cc2olx.xml import cc_xml


class LtiContentProcessor(AbstractContentProcessor):
    """
    LTI content processor.
    """

    DEFAULT_WIDTH = "500"
    DEFAULT_HEIGHT = "500"

    def process(self, resource: dict, idref: str) -> Optional[List[xml.dom.minidom.Element]]:
        if content := self._parse(resource, idref):
            self._context.add_lti_consumer_id(content["lti_id"])
            return self._create_nodes(content)
        return None

    def _parse(self, resource: dict, idref: str) -> Optional[dict]:
        """
        Parse the resource content.
        """
        if re.match(CommonCartridgeResourceType.LTI_LINK, resource["type"]):
            data = self._parse_lti(resource)
            # Canvas flavored courses have correct url in module meta for lti links
            if self._cartridge.is_canvas_flavor:
                if item_data := self._cartridge.module_meta.get_external_tool_item_data(idref):
                    data["launch_url"] = item_data.get("url", data["launch_url"])
            return data
        return None

    def _parse_lti(self, resource: dict) -> dict:
        """
        Parse LTI resource.
        """
        resource_file = resource["children"][0]
        resource_file_path = self._cartridge.build_resource_file_path(resource_file.href)
        tree = filesystem.get_xml_tree(resource_file_path)
        root = tree.getroot()
        title = root.title.text

        return {
            "title": title,
            "description": root.description.text,
            "launch_url": self._parse_launch_url(root),
            "height": self._parse_height(root),
            "width": self._parse_width(root),
            "custom_parameters": self._parse_custom_parameters(root),
            "lti_id": self._parse_lti_id(root, title),
        }

    def _parse_launch_url(self, resource_root: cc_xml.BasicLtiLink) -> str:
        """
        Parse URL to launch LTI.
        """
        if (launch_url := resource_root.secure_launch_url) is None:
            launch_url = resource_root.launch_url
        return getattr(launch_url, "text", "")

    def _parse_width(self, resource_root: cc_xml.BasicLtiLink) -> str:
        """
        Parse width.
        """
        return getattr(resource_root.width, "text", self.DEFAULT_WIDTH)

    def _parse_height(self, resource_root: cc_xml.BasicLtiLink) -> str:
        """
        Parse height.
        """
        return getattr(resource_root.height, "text", self.DEFAULT_HEIGHT)

    def _parse_custom_parameters(self, resource_root: cc_xml.BasicLtiLink) -> Dict[str, str]:
        """
        Parse custom parameters.
        """
        custom = resource_root.custom
        return {} if custom is None else {option.get("name"): option.text for option in custom}

    def _parse_lti_id(self, resource_root: cc_xml.BasicLtiLink, title: str) -> str:
        """
        Parse LTI identifier.

        For Canvas flavored CC, tool_id is used as lti_id if present.
        """
        tool_id = resource_root.canvas_tool_id
        return simple_slug(title) if tool_id is None else tool_id.text

    def _create_nodes(self, content: dict) -> List[xml.dom.minidom.Element]:
        """
        Give out <lti_consumer> OLX nodes.
        """
        doc = xml.dom.minidom.Document()
        el = element_builder(doc)

        custom_parameters = "[{params}]".format(
            params=", ".join(
                [
                    '"{key}={value}"'.format(
                        key=key,
                        value=value,
                    )
                    for key, value in content["custom_parameters"].items()
                ]
            ),
        )
        lti_consumer_node = el(
            "lti_consumer",
            [],
            {
                "custom_parameters": custom_parameters,
                "description": content["description"],
                "display_name": content["title"],
                "inline_height": content["height"],
                "inline_width": content["width"],
                "launch_url": content["launch_url"],
                "modal_height": content["height"],
                "modal_width": content["width"],
                "xblock-family": "xblock.v1",
                "lti_id": content["lti_id"],
            },
        )
        return [lti_consumer_node]
