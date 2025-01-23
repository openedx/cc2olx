import xml.dom.minidom
from typing import List

from cc2olx.olx_generators import AbstractOlxGenerator
from cc2olx.utils import element_builder


class VideoOlxGenerator(AbstractOlxGenerator):
    """
    Generate OLX for video content.
    """

    def create_nodes(self, content: dict) -> List[xml.dom.minidom.Element]:
        xml_element = element_builder(self._doc)
        youtube_video_id = content["youtube"]
        attributes = {"youtube": f"1.00:{youtube_video_id}", "youtube_id_1_0": content["youtube"]}
        video_element = xml_element("video", children=None, attributes=attributes)
        return [video_element]
