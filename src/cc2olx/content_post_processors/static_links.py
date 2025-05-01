import html as html_parser
import re
import urllib
import xml.dom.minidom
from functools import cached_property, singledispatchmethod
from typing import Callable, List, NamedTuple, Tuple

from cc2olx.content_post_processors import AbstractContentPostProcessor
from cc2olx.logging import build_console_logger
from cc2olx.utils import get_xml_minidom_element_iterator

console_logger = build_console_logger(__name__)


class LinkKeywordProcessor(NamedTuple):
    """
    Encapsulate a keyword inside a static link and its processor.
    """

    keyword: str
    processor: Callable[[str, str], str]


class StaticLinkPostProcessor(AbstractContentPostProcessor):
    """
    Provide static links processing functionality.
    """

    LINK_ATTRIBUTES = ("src", "href")
    HTML_LINK_PATTERN = re.compile(r'(?:src|href)\s*=\s*"(.+?)"')

    def process(self, element: xml.dom.minidom.Element) -> None:
        """
        Turn Common Cartridge static links into OLX static links in the element.
        """
        for node in get_xml_minidom_element_iterator(element):
            self._process_node_links(node)

    @singledispatchmethod
    def _process_node_links(self, node: xml.dom.minidom.Node) -> None:
        """
        Process node static links.
        """

    @_process_node_links.register
    def _(self, node: xml.dom.minidom.Text) -> None:
        """
        Process static links in a text node.
        """
        links = re.findall(self.HTML_LINK_PATTERN, node.nodeValue)
        node.nodeValue = self.process_html_links(node.nodeValue, links)

    @_process_node_links.register
    def _(self, node: xml.dom.minidom.Element) -> None:
        """
        Process static links in an `Element` node.
        """
        for attribute_name in self.LINK_ATTRIBUTES:
            if link := node.getAttribute(attribute_name):
                node.setAttribute(attribute_name, self.process_html_links(link, [link]))

    def process_html_links(self, html: str, links: List[str]) -> str:
        """
        Process the provided links inside HTML string.
        """
        for link in links:
            for keyword, processor in self._link_keyword_processors:
                if keyword in link:
                    html = processor(link, html)
                    break
            else:
                html = self._process_relative_external_links(link, html)

        return html

    @cached_property
    def _link_keyword_processors(self) -> Tuple[LinkKeywordProcessor, ...]:
        """
        Provide link keyword processors.
        """
        return (
            LinkKeywordProcessor("IMS-CC-FILEBASE", self._process_ims_cc_filebase),
            LinkKeywordProcessor("WIKI_REFERENCE", self._process_wiki_reference),
            LinkKeywordProcessor("external_tools", self._process_external_tools_link),
            LinkKeywordProcessor("CANVAS_OBJECT_REFERENCE", self._process_canvas_reference),
        )

    def _process_wiki_reference(self, link: str, html: str) -> str:
        """
        Replace $WIKI_REFERENCE$ with edx /jump_to_id/<url_name>.
        """
        search_key = urllib.parse.unquote(link).replace("$WIKI_REFERENCE$/pages/", "")

        # remove query params and add suffix .html to match with resource_id_by_href
        search_key = search_key.split("?")[0] + ".html"
        for key in self._cartridge.resource_id_by_href.keys():
            if key.endswith(search_key):
                replace_with = "/jump_to_id/{}".format(self._cartridge.resource_id_by_href[key])
                return html.replace(link, replace_with)

        console_logger.warning("Unable to process Wiki link - %s", link)
        return html

    @staticmethod
    def _process_canvas_reference(link: str, html: str) -> str:
        """
        Replace $CANVAS_OBJECT_REFERENCE$ with edx /jump_to_id/<url_name>.
        """
        object_id = urllib.parse.unquote(link).replace("$CANVAS_OBJECT_REFERENCE$/quizzes/", "/jump_to_id/")
        return html.replace(link, object_id)

    @staticmethod
    def _process_ims_cc_filebase(link: str, html: str) -> str:
        """
        Replace $IMS-CC-FILEBASE$ with /static.
        """
        new_link = urllib.parse.unquote(link).replace("$IMS-CC-FILEBASE$", "/static")
        # skip query parameters for static files
        new_link = new_link.split("?")[0]
        # &amp; is not valid in an URL. But some file seem to have it when it should be &
        new_link = new_link.replace("&amp;", "&")
        return html.replace(link, new_link)

    @staticmethod
    def _process_external_tools_link(link: str, html: str) -> str:
        """
        Replace $CANVAS_OBJECT_REFERENCE$/external_tools/retrieve with appropriate external link.
        """
        external_tool_query = urllib.parse.urlparse(link).query
        # unescape query that has been HTML encoded so it can be parsed correctly
        unescaped_external_tool_query = html_parser.unescape(external_tool_query)
        external_tool_url = urllib.parse.parse_qs(unescaped_external_tool_query).get("url", [""])[0]
        return html.replace(link, external_tool_url)

    def _process_relative_external_links(self, link: str, html: str) -> str:
        """
        Turn static file URLs outside OLX_STATIC_DIR into absolute URLs.

        Allow to avoid a situation when the original course page links have
        relative URLs, such URLs weren't included into the exported Common
        Cartridge course file that causes broken URLs in the imported OeX
        course. The function adds the origin source to URLs to make them
        absolute ones.
        """
        if self._context.relative_links_source is None or link in self._cartridge.olx_to_original_static_file_paths.all:
            return html

        url = urllib.parse.urljoin(self._context.relative_links_source, link)
        return html.replace(link, url)
