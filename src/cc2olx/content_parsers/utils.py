import html as html_parser
import logging
import re
import urllib
from typing import TypeVar, Optional

from cc2olx.dataclasses import LinkKeywordProcessor
from cc2olx.models import Cartridge

logger = logging.getLogger()

Content = TypeVar("Content")


class StaticLinkProcessor:
    """
    Provide static links processing functionality.
    """

    def __init__(self, cartridge: Cartridge, relative_links_source: Optional[str]) -> None:
        self._cartridge = cartridge
        self._relative_links_source = relative_links_source

    def process_content_static_links(self, content: Content) -> Content:
        """
        Take a node data and recursively find and escape static links.

        Provide detail data with static link escaped to an OLX-friendly format.
        """

        if isinstance(content, str):
            return self.process_static_links(content)

        if isinstance(content, list):
            for index, value in enumerate(content):
                content[index] = self.process_content_static_links(value)
        elif isinstance(content, dict):
            for key, value in content.items():
                content[key] = self.process_content_static_links(value)

        return content

    def process_static_links(self, html: str) -> str:
        """
        Process static links like src and href to have appropriate links.
        """
        items = re.findall(r'(src|href)\s*=\s*"(.+?)"', html)

        link_keyword_processors = (
            LinkKeywordProcessor("IMS-CC-FILEBASE", self._process_ims_cc_filebase),
            LinkKeywordProcessor("WIKI_REFERENCE", self._process_wiki_reference),
            LinkKeywordProcessor("external_tools", self._process_external_tools_link),
            LinkKeywordProcessor("CANVAS_OBJECT_REFERENCE", self._process_canvas_reference),
        )

        for _, link in items:
            for keyword, processor in link_keyword_processors:
                if keyword in link:
                    html = processor(link, html)
                    break
            else:
                html = self._process_relative_external_links(link, html)

        return html

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

        logger.warning("Unable to process Wiki link - %s", link)
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
        if self._relative_links_source is None or link in self._cartridge.olx_to_original_static_file_paths.all:
            return html

        url = urllib.parse.urljoin(self._relative_links_source, link)
        return html.replace(link, url)
