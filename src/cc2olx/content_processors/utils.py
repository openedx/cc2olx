import re
import xml.dom.minidom
from typing import Dict, List, Optional, Type

from django.conf import settings
from django.utils.module_loading import import_string

from cc2olx import filesystem
from cc2olx.content_processors import AbstractContentProcessor
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.models import Cartridge
from cc2olx.utils import element_builder


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


def generate_default_ora_criteria() -> List[xml.dom.minidom.Element]:
    """
    Generate default ORA criteria OLX.
    """
    doc = xml.dom.minidom.Document()
    el = element_builder(doc)

    return [
        el(
            "criterion",
            [
                el("name", "Ideas"),
                el("label", "Ideas"),
                el("prompt", "Determine if there is a unifying theme or main idea."),
                el(
                    "option",
                    [
                        el("name", "Poor"),
                        el("label", "Poor"),
                        el(
                            "explanation",
                            "Difficult for the reader to discern the main idea. Too brief or too repetitive to "
                            "establish or maintain a focus.",
                        ),
                    ],
                    {"points": "0"},
                ),
                el(
                    "option",
                    [
                        el("name", "Fair"),
                        el("label", "Fair"),
                        el(
                            "explanation",
                            "Presents a unifying theme or main idea, but may include minor tangents. Stays "
                            "somewhat focused on topic and task.",
                        ),
                    ],
                    {"points": "3"},
                ),
                el(
                    "option",
                    [
                        el("name", "Good"),
                        el("label", "Good"),
                        el(
                            "explanation",
                            "Presents a unifying theme or main idea without going off on tangents. Stays "
                            "completely focused on topic and task.",
                        ),
                    ],
                    {"points": "5"},
                ),
            ],
            {"feedback": "optional"},
        ),
        el(
            "criterion",
            [
                el("name", "Content"),
                el("label", "Content"),
                el("prompt", "Assess the content of the submission"),
                el(
                    "option",
                    [
                        el("name", "Poor"),
                        el("label", "Poor"),
                        el(
                            "explanation",
                            "Includes little information with few or no details or unrelated details. Unsuccessful "
                            "in attempts to explore any facets of the topic.",
                        ),
                    ],
                    {"points": "0"},
                ),
                el(
                    "option",
                    [
                        el("name", "Fair"),
                        el("label", "Fair"),
                        el(
                            "explanation",
                            "Includes little information and few or no details. Explores only one or two facets of "
                            "the topic.",
                        ),
                    ],
                    {"points": "1"},
                ),
                el(
                    "option",
                    [
                        el("name", "Good"),
                        el("label", "Good"),
                        el(
                            "explanation",
                            "Includes sufficient information and supporting details. (Details may not be fully "
                            "developed; ideas may be listed.) Explores some facets of the topic.",
                        ),
                    ],
                    {"points": "3"},
                ),
                el(
                    "option",
                    [
                        el("name", "Excellent"),
                        el("label", "Excellent"),
                        el(
                            "explanation",
                            "Includes in-depth information and exceptional supporting details that are fully "
                            "developed. Explores all facets of the topic.",
                        ),
                    ],
                    {"points": "5"},
                ),
            ],
            {"feedback": "optional"},
        ),
    ]
