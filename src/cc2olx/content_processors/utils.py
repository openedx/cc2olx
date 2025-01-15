import re
from typing import Dict, List, Optional, Type

from django.conf import settings
from django.utils.module_loading import import_string

from cc2olx import filesystem
from cc2olx.content_processors import AbstractContentProcessor
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.models import Cartridge


def parse_web_link_content(resource: dict, cartridge: Cartridge) -> Optional[Dict[str, str]]:
    """
    Provide Web Link resource data.
    """
    resource_type = resource["type"]
    if re.match(CommonCartridgeResourceType.WEB_LINK, resource_type):
        resource_file = resource["children"][0]
        resource_file_path = cartridge.build_resource_file_path(resource_file.href)
        tree = filesystem.get_xml_tree(resource_file_path)
        root = tree.getroot()
        return {
            "href": root.get_url(resource_type).get("href"),
            "text": root.get_title(resource_type).text,
        }
    return None


def load_content_processor_types() -> List[Type[AbstractContentProcessor]]:
    """
    Load content processor types.
    """
    return [import_string(processor_path) for processor_path in settings.CONTENT_PROCESSORS]
