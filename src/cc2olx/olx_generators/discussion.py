import xml.dom.minidom
from typing import List

from cc2olx.olx_generators import AbstractOlxGenerator
from cc2olx.utils import clean_from_cdata, element_builder


class DiscussionOlxGenerator(AbstractOlxGenerator):
    """
    Generate OLX for discussions.
    """

    DEFAULT_TEXT = "MISSING CONTENT"

    def create_nodes(self, content: dict) -> List[xml.dom.minidom.Element]:
        el = element_builder(self._doc)

        txt = self.DEFAULT_TEXT if content["text"] is None else content["text"]
        txt = clean_from_cdata(txt)
        html_node = el("html", [self._doc.createCDATASection(txt)], {})

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
