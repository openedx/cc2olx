import re
import xml.dom.minidom
from typing import Dict, List, Optional

from cc2olx.content_processors import AbstractContentProcessor
from cc2olx.content_processors.utils import parse_web_link_content
from cc2olx.utils import element_builder

YOUTUBE_LINK_PATTERN = r"youtube.com/watch\?v=(?P<video_id>[-\w]+)"


class VideoContentProcessor(AbstractContentProcessor):
    """
    Video content processor.
    """

    def process(self, resource: dict, idref: str) -> Optional[List[xml.dom.minidom.Element]]:
        if content := self._parse(resource):
            return self._create_nodes(content)
        return None

    def _parse(self, resource: dict) -> Optional[Dict[str, str]]:
        """
        Parse the resource content.
        """
        if web_link_content := parse_web_link_content(resource, self._cartridge):
            if youtube_match := re.search(YOUTUBE_LINK_PATTERN, web_link_content["href"]):
                return {"youtube": youtube_match.group("video_id")}
        return None

    def _create_nodes(self, content: Dict[str, str]) -> List[xml.dom.minidom.Element]:
        """
        Give out <video> OLX nodes.
        """
        doc = xml.dom.minidom.Document()
        xml_element = element_builder(doc)
        youtube_video_id = content["youtube"]
        attributes = {"youtube": f"1.00:{youtube_video_id}", "youtube_id_1_0": youtube_video_id}
        video_element = xml_element("video", children=None, attributes=attributes)
        return [video_element]
