import html
import re
import xml.dom.minidom
from typing import Dict, List, Optional

from lxml import etree

from cc2olx.content_processors import AbstractContentProcessor
from cc2olx.content_processors.utils import parse_web_link_content
from cc2olx.enums import SupportedCustomBlockContentType
from cc2olx.utils import element_builder


class GoogleDocumentContentProcessor(AbstractContentProcessor):
    """
    Google document content parser.

    For resources that represent a Google document (documents/spreadsheets/
    presentations/forms etc.) except drawings, generate the Google Drive xBlock
    (https://github.com/openedx/xblock-google-drive) OLX to display the
    document on the course page directly.
    """

    SUPPORTED_GOOGLE_DOCUMENT_URL_PATTERN = r"^https?:\/\/docs\.google\.com\/(?!drawings\/)([^\/]+)\/d\/.*$"
    # Standard iframe settings added by Google document xBlock by default.
    DEFAULT_GOOGLE_DOCUMENT_IFRAME_ATTRIBUTES = {
        "frameborder": "0",
        "width": "960",
        "height": "569",
        "allowfullscreen": "true",
        "mozallowfullscreen": "true",
        "webkitallowfullscreen": "true",
    }

    def process(self, resource: dict, idref: str) -> Optional[List[xml.dom.minidom.Element]]:
        if not self._context.is_content_type_with_custom_block_used(SupportedCustomBlockContentType.GOOGLE_DOCUMENT):
            return None

        if content := self._parse(resource):
            return self._create_nodes(content)
        return None

    def _parse(self, resource: dict) -> Optional[dict]:
        """
        Parse the resource content.
        """
        if web_link_content := parse_web_link_content(resource, self._cartridge):
            return self._transform_web_link_content_to_google_document(web_link_content)
        return None

    def _transform_web_link_content_to_google_document(
        self,
        web_link_content: Dict[str, str],
    ) -> Optional[Dict[str, str]]:
        """
        Build Google document block data from Web Link resource data.
        """
        web_link_url = web_link_content["href"]
        return (
            {"url": web_link_url} if re.match(self.SUPPORTED_GOOGLE_DOCUMENT_URL_PATTERN, web_link_url, re.I) else None
        )

    def _create_nodes(self, content: dict) -> List[xml.dom.minidom.Element]:
        """
        Give out <google-document> OLX nodes.
        """
        doc = xml.dom.minidom.Document()
        el = element_builder(doc)
        google_document_node = el("google-document", [], self._generate_google_document_attributes(content))
        return [google_document_node]

    def _generate_google_document_attributes(self, content: Dict[str, str]) -> Dict[str, str]:
        """
        Generate Google document tag attributes.
        """
        google_document_iframe = self._create_google_document_iframe(content)
        google_document_iframe_string = html.unescape(
            etree.tostring(google_document_iframe, pretty_print=True, method="html").decode("utf-8")
        )
        return {"embed_code": google_document_iframe_string}

    def _create_google_document_iframe(self, content: Dict[str, str]) -> etree.ElementBase:
        """
        Create HTML iframe tag pointing to Google document.
        """
        return etree.Element("iframe", self._generate_google_document_iframe_attributes(content))

    def _generate_google_document_iframe_attributes(self, content: Dict[str, str]) -> Dict[str, str]:
        """
        Generate Google document HTML iframe tag attributes.
        """
        return {
            **self.DEFAULT_GOOGLE_DOCUMENT_IFRAME_ATTRIBUTES,
            "src": content["url"],
        }
