import urllib
import xml.dom.minidom
from typing import Dict, List, Optional

from cc2olx.content_processors import AbstractContentProcessor
from cc2olx.content_processors.utils import WebContentFile, parse_web_link_content
from cc2olx.enums import CommonCartridgeResourceType, SupportedCustomBlockContentType
from cc2olx.utils import element_builder


class PDFContentProcessor(AbstractContentProcessor):
    """
    PDF content processor.

    For resources that represent a PDF document, generate the PDF xBlock
    (https://github.com/raccoongang/xblock-pdf) OLX to display the document on
    the course page directly.
    """

    def process(self, resource: dict, idref: str) -> Optional[List[xml.dom.minidom.Element]]:
        if not self._context.is_content_type_with_custom_block_used(SupportedCustomBlockContentType.PDF):
            return None

        if content := self._parse(resource):
            return self._create_nodes(content)
        return None

    def _parse(self, resource: dict) -> Optional[dict]:
        """
        Parse the resource content.
        """
        if resource["type"] == CommonCartridgeResourceType.WEB_CONTENT:
            return self._parse_webcontent(resource)
        elif web_link_content := parse_web_link_content(resource, self._cartridge):
            return self._transform_web_link_content_to_pdf(web_link_content)
        return None

    def _parse_webcontent(self, resource: dict) -> Optional[Dict[str, str]]:
        """
        Parse the resource with "webcontent" type.
        """
        web_content_file = WebContentFile(self._cartridge, resource["children"][0])
        resource_file_path = web_content_file.resource_file_path

        if resource_file_path.suffix in SupportedCustomBlockContentType.PDF.file_extensions:
            return (
                self._parse_pdf_webcontent_from_web_resources_dir(web_content_file)
                if web_content_file.is_from_web_resources_dir()
                else self._parse_pdf_webcontent_outside_web_resources_dir(web_content_file)
            )
        return None

    def _parse_pdf_webcontent_from_web_resources_dir(self, web_content_file: WebContentFile) -> Dict[str, str]:
        """
        Parse webcontent PDF file from "web_resources" directory.
        """
        olx_static_path = web_content_file.olx_static_path
        self._cartridge.olx_to_original_static_file_paths.add_web_resource_path(
            olx_static_path,
            web_content_file.resource_file_path,
        )
        return {"url": olx_static_path}

    def _parse_pdf_webcontent_outside_web_resources_dir(self, web_content_file: WebContentFile) -> Dict[str, str]:
        """
        Parse webcontent PDF file located outside "web_resources" directory.
        """
        olx_static_path = web_content_file.olx_static_path
        self._cartridge.olx_to_original_static_file_paths.add_extra_path(
            olx_static_path,
            web_content_file.resource_relative_path,
        )
        return {"url": olx_static_path}

    @staticmethod
    def _transform_web_link_content_to_pdf(web_link_content: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Build PDF block data from Web Link resource data.
        """
        web_link_url = web_link_content["href"]
        does_web_link_point_to_pdf_file = any(
            urllib.parse.urlparse(web_link_url).path.endswith(file_extension)
            for file_extension in SupportedCustomBlockContentType.PDF.file_extensions
        )
        return {"url": web_link_url} if does_web_link_point_to_pdf_file else None

    def _create_nodes(self, content: dict) -> List[xml.dom.minidom.Element]:
        """
        Give out <pdf> OLX nodes.
        """
        doc = xml.dom.minidom.Document()
        el = element_builder(doc)

        pdf_node = el("pdf", [], {"url": content["url"]})
        return [pdf_node]
