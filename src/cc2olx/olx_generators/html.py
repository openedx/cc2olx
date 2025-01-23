import xml.dom.minidom
from typing import List, Tuple

import lxml.html

from cc2olx.olx_generators import AbstractOlxGenerator
from cc2olx.utils import clean_from_cdata


class HtmlOlxGenerator(AbstractOlxGenerator):
    """
    Generate OLX for HTML content.
    """

    def create_nodes(self, content: dict) -> List[xml.dom.minidom.Element]:
        """
        Process the HTML and gives out corresponding HTML or Video OLX nodes.
        """
        video_olx = []
        nodes = []
        html = content["html"]
        if self._context.iframe_link_parser:
            html, video_olx = self._process_html_for_iframe(html)
        html = clean_from_cdata(html)
        txt = self._doc.createCDATASection(html)

        html_node = self._doc.createElement("html")
        html_node.appendChild(txt)
        nodes.append(html_node)

        nodes.extend(video_olx)

        return nodes

    def _process_html_for_iframe(self, html_str: str) -> Tuple[str, List[xml.dom.minidom.Element]]:
        """
        Parse the iframe with embedded video, to be converted into video xblock.

        Provide the html content of the file, if iframe is present and
        converted into xblock then iframe is removed from the HTML, as well as
        a list of XML children, i.e video xblock.
        """
        video_olx = []
        parsed_html = lxml.html.fromstring(html_str)
        iframes = parsed_html.xpath("//iframe")
        if not iframes:
            return html_str, video_olx

        video_olx, converted_iframes = self._context.iframe_link_parser.get_video_olx(self._doc, iframes)
        if video_olx:
            # If video xblock is present then we modify the HTML to remove the iframe
            # hence we need to convert the modified HTML back to string. We also remove
            # the parent if there are no other children.
            for iframe in converted_iframes:
                parent = iframe.getparent()
                parent.remove(iframe)
                if not parent.getchildren():
                    parent.getparent().remove(parent)
            return lxml.html.tostring(parsed_html).decode("utf-8"), video_olx
        return html_str, video_olx
