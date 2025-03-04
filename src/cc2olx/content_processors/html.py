import imghdr
import logging
import re
import xml.dom.minidom
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import lxml.html
from django.conf import settings

from cc2olx.constants import FALLBACK_OLX_CONTENT, OLX_STATIC_PATH_TEMPLATE
from cc2olx.content_processors import AbstractContentProcessor
from cc2olx.content_processors.utils import parse_web_link_content
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.utils import clean_from_cdata

logger = logging.getLogger()

HTML_FILENAME_SUFFIX = ".html"
LINK_HTML = '<a href="{url}">{text}</a>'
WEB_RESOURCES_DIR_NAME = "web_resources"


class HtmlContentProcessor(AbstractContentProcessor):
    """
    HTML content processor.
    """

    FALLBACK_CONTENT = {"html": FALLBACK_OLX_CONTENT}

    def process(self, resource: dict, idref: str) -> Optional[List[xml.dom.minidom.Element]]:
        content = self._parse(resource, idref)
        return self._create_nodes(content)

    def _parse(self, resource: dict, idref: str) -> Dict[str, str]:
        """
        Parse content of the resource with the specified identifier.
        """
        resource_type = resource["type"]

        if resource_type == CommonCartridgeResourceType.WEB_CONTENT:
            content = self._parse_webcontent(resource, idref)
        elif re.match(CommonCartridgeResourceType.WEB_LINK, resource_type):
            web_link_content = parse_web_link_content(resource, self._cartridge)
            content = self._transform_web_link_content_to_html(web_link_content)
        elif self.is_known_unprocessed_resource_type(resource_type):
            content = self.FALLBACK_CONTENT
        else:
            content = self._parse_not_imported_content(resource)
        return content

    def _parse_webcontent(self, resource: dict, idref: str) -> Dict[str, str]:
        """
        Parse the resource with "webcontent" type.
        """
        resource_file = resource["children"][0]
        resource_relative_link = resource_file.href
        resource_file_path = self._cartridge.build_resource_file_path(resource_relative_link)

        if resource_file_path.suffix == HTML_FILENAME_SUFFIX:
            content = self._parse_webcontent_html_file(resource_file_path, idref)
        elif WEB_RESOURCES_DIR_NAME in str(resource_file_path) and imghdr.what(str(resource_file_path)):
            content = self._parse_image_webcontent_from_web_resources_dir(resource_file_path)
        elif WEB_RESOURCES_DIR_NAME not in str(resource_file_path):
            content = self._parse_webcontent_outside_web_resources_dir(resource_relative_link)
        else:
            logger.info("Skipping webcontent: %s", resource_file_path)
            content = self.FALLBACK_CONTENT

        return content

    @staticmethod
    def _parse_webcontent_html_file(resource_file_path: Path, idref: str) -> Dict[str, str]:
        """
        Parse webcontent HTML file.
        """
        try:
            with open(resource_file_path, encoding="utf-8") as resource_file:
                html = resource_file.read()
        except:  # noqa: E722
            logger.error("Failure reading %s from id %s", resource_file_path, idref)
            raise
        return {"html": html}

    def _parse_image_webcontent_from_web_resources_dir(self, resource_file_path: Path) -> Dict[str, str]:
        """
        Parse webcontent image from "web_resources" directory.
        """
        static_filename = str(resource_file_path).split(f"{WEB_RESOURCES_DIR_NAME}/")[1]
        olx_static_path = OLX_STATIC_PATH_TEMPLATE.format(static_filename=static_filename)
        self._cartridge.olx_to_original_static_file_paths.add_web_resource_path(olx_static_path, resource_file_path)
        image_webcontent_tpl_path = settings.TEMPLATES_DIR / "image_webcontent.html"

        with open(image_webcontent_tpl_path, encoding="utf-8") as image_webcontent_tpl:
            tpl_content = image_webcontent_tpl.read()
            html = tpl_content.format(olx_static_path=olx_static_path, static_filename=static_filename)

        return {"html": html}

    def _parse_webcontent_outside_web_resources_dir(self, resource_relative_path: str) -> Dict[str, str]:
        """
        Parse webcontent located outside "web_resources" directory.
        """
        # This webcontent is outside ``web_resources`` directory
        # So we need to manually copy it to OLX_STATIC_DIR
        olx_static_path = OLX_STATIC_PATH_TEMPLATE.format(static_filename=resource_relative_path)
        self._cartridge.olx_to_original_static_file_paths.add_extra_path(olx_static_path, resource_relative_path)
        external_webcontent_tpl_path = settings.TEMPLATES_DIR / "external_webcontent.html"

        with open(external_webcontent_tpl_path, encoding="utf-8") as external_webcontent_tpl:
            tpl_content = external_webcontent_tpl.read()
            html = tpl_content.format(olx_static_path=olx_static_path, resource_relative_path=resource_relative_path)

        return {"html": html}

    @staticmethod
    def _transform_web_link_content_to_html(web_link_content: Dict[str, str]) -> Dict[str, str]:
        """
        Generate HTML for weblink.
        """
        video_link_html = LINK_HTML.format(url=web_link_content["href"], text=web_link_content.get("text", ""))
        return {"html": video_link_html}

    @staticmethod
    def is_known_unprocessed_resource_type(resource_type: str) -> bool:
        """
        Decides whether the resource type is a known CC type to be unprocessed.
        """
        return any(
            re.match(type_pattern, resource_type)
            for type_pattern in (
                CommonCartridgeResourceType.LTI_LINK,
                CommonCartridgeResourceType.QTI_ASSESSMENT,
                CommonCartridgeResourceType.DISCUSSION_TOPIC,
                CommonCartridgeResourceType.ASSIGNMENT,
            )
        )

    @staticmethod
    def _parse_not_imported_content(resource: dict) -> Dict[str, str]:
        """
        Parse the resource which content type cannot be processed.
        """
        resource_type = resource["type"]
        text = f"Not imported content: type = {resource_type!r}"
        if "href" in resource:
            text += ", href = {!r}".format(resource["href"])

        logger.info("%s", text)
        return {"html": text}

    def _create_nodes(self, content: Dict[str, str]) -> List[xml.dom.minidom.Element]:
        """
        Give out <html> or <video> OLX nodes.
        """
        video_olx = []
        nodes = []
        html = content["html"]
        doc = xml.dom.minidom.Document()

        if self._context.iframe_link_parser:
            html, video_olx = self._process_html_for_iframe(html, doc)
        html = clean_from_cdata(html)
        txt = doc.createCDATASection(html)

        html_node = doc.createElement("html")
        html_node.appendChild(txt)
        nodes.append(html_node)

        nodes.extend(video_olx)

        return nodes

    def _process_html_for_iframe(
        self,
        html_str: str,
        doc: xml.dom.minidom.Document,
    ) -> Tuple[str, List[xml.dom.minidom.Element]]:
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

        video_olx, converted_iframes = self._context.iframe_link_parser.get_video_olx(doc, iframes)
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
