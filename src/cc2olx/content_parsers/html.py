import imghdr
import logging
import re
from pathlib import Path
from typing import Dict, Optional

from django.conf import settings

from cc2olx.constants import LINK_HTML, OLX_STATIC_PATH_TEMPLATE, WEB_RESOURCES_DIR_NAME
from cc2olx.content_parsers import AbstractContentParser
from cc2olx.content_parsers.mixins import WebLinkParserMixin
from cc2olx.enums import CommonCartridgeResourceType

logger = logging.getLogger()

HTML_FILENAME_SUFFIX = ".html"


class HtmlContentParser(WebLinkParserMixin, AbstractContentParser):
    """
    HTML resource content parser.
    """

    DEFAULT_CONTENT = {"html": "<p>MISSING CONTENT</p>"}

    def _parse_content(self, idref: Optional[str]) -> Dict[str, str]:
        if idref:
            resource = self._cartridge.define_resource(idref)
            if resource is None:
                logger.info("Missing resource: %s", idref)
                content = self.DEFAULT_CONTENT
            elif resource["type"] == CommonCartridgeResourceType.WEB_CONTENT:
                content = self._parse_webcontent(idref, resource)
            elif web_link_content := self._parse_web_link_content(resource):
                content = self._transform_web_link_content_to_html(web_link_content)
            elif self.is_known_unprocessed_resource_type(resource["type"]):
                content = self.DEFAULT_CONTENT
            else:
                content = self._parse_not_imported_content(resource)
            return content
        return self.DEFAULT_CONTENT

    def _parse_webcontent(self, idref: str, resource: dict) -> Dict[str, str]:
        """
        Parse the resource with "webcontent" type.
        """
        resource_file = resource["children"][0]
        resource_relative_link = resource_file.href
        resource_file_path = self._cartridge.build_resource_file_path(resource_relative_link)

        if resource_file_path.suffix == HTML_FILENAME_SUFFIX:
            content = self._parse_webcontent_html_file(idref, resource_file_path)
        elif WEB_RESOURCES_DIR_NAME in str(resource_file_path) and imghdr.what(str(resource_file_path)):
            content = self._parse_image_webcontent_from_web_resources_dir(resource_file_path)
        elif WEB_RESOURCES_DIR_NAME not in str(resource_file_path):
            content = self._parse_webcontent_outside_web_resources_dir(resource_relative_link)
        else:
            logger.info("Skipping webcontent: %s", resource_file_path)
            content = self.DEFAULT_CONTENT

        return content

    @staticmethod
    def _parse_webcontent_html_file(idref: str, resource_file_path: Path) -> Dict[str, str]:
        """
        Parse webcontent HTML file.
        """
        try:
            with open(resource_file_path, encoding="utf-8") as resource_file:
                html = resource_file.read()
        except:  # noqa: E722
            logger.error("Failure reading %s from id %s", resource_file_path, idref)  # noqa: E722
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
