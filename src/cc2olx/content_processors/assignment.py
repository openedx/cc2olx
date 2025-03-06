import re
import xml.dom.minidom
from enum import Enum
from typing import Dict, Optional, List, Set, Union

from cc2olx import filesystem
from cc2olx.content_processors import AbstractContentProcessor
from cc2olx.content_processors.utils import generate_default_ora_criteria
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.utils import element_builder
from cc2olx.xml import cc_xml


class AssignmentSubmissionFormatType(str, Enum):
    """
    Enumerate possible submission format types for CC assignments.
    """

    FILE = "file"
    HTML = "html"
    TEXT = "text"
    URL = "url"


class AssignmentContentProcessor(AbstractContentProcessor):
    """
    Assignment content processor.

    Process Common Cartridge Assignment Extension Resource (its data model
    description: https://www.imsglobal.org/cc/ccv1p3/AssignmentContentType.html)
    by parsing the CC Assignment XML and producing OLX Open Response
    Assessment (ORA) blocks. Assignments are problems that require a written
    response from a student, an answer in the form of a file, a link to a
    resource with the solution (or a combination of these response types) and
    cannot be graded automatically.
    Assignment maps to ORA not completely: Assignment has attachments but ORA
    does not, ORA has rubrics, but Assignments do not. So, only similar
    functionalities are processed, for some missed Assignment features ORA
    defaults are provided.
    """

    DEFAULT_ACCEPTED_FORMAT_TYPES = {AssignmentSubmissionFormatType.HTML, AssignmentSubmissionFormatType.FILE}
    DEFAULT_FILE_UPLOAD_TYPE = "pdf-and-image"
    DEFAULT_WHITE_LISTED_FILE_TYPES = ["pdf", "gif", "jpg", "jpeg", "jfif", "pjpeg", "pjp", "png"]

    def process(self, resource: dict, idref: str) -> Optional[List[xml.dom.minidom.Element]]:
        if content := self._parse(resource):
            return self._create_nodes(content)
        return None

    def _parse(self, resource: dict) -> Optional[dict]:
        """
        Parse the resource content.
        """
        if re.match(CommonCartridgeResourceType.ASSIGNMENT, resource["type"]):
            return self._parse_assignment(resource)
        return None

    def _parse_assignment(self, resource: dict) -> Dict[str, Union[bool, str, List[str]]]:
        """
        Parse the assignment resource.

        Take the resource data dictionary and extract from it data required for
        ORA blocks creation, along with some defaults that are not specified in
        Common Cartridge specification. Produce the dictionary with this data.
        """
        resource_file = resource["children"][0]
        tree = filesystem.get_xml_tree(self._cartridge.build_resource_file_path(resource_file.href))
        root = tree.getroot()

        return {
            "title": root.title.text,
            **self._parse_response_data(root),
            **self._parse_prompt_data(root),
        }

    def _parse_prompt_data(self, resource_root: cc_xml.AssignmentElement) -> Dict[str, str]:
        """
        Parse prompt-related data.
        """
        prompt_element = self._define_prompt_element(resource_root)

        return {
            "prompt": getattr(prompt_element, "text", ""),
            "prompts_type": self._define_prompts_type(prompt_element),
        }

    @staticmethod
    def _define_prompt_element(resource_root: cc_xml.AssignmentElement) -> cc_xml.CommonCartridgeElementBase:
        """
        Define the element containing prompt data.
        """
        text = resource_root.get_text()
        return text if text is not None else resource_root.instructor_text

    @staticmethod
    def _define_prompts_type(prompt_element: cc_xml.CommonCartridgeElementBase) -> str:
        """
        Define prompts type.
        """
        raw_prompt_type = prompt_element.attrib["texttype"] if prompt_element is not None else "text/plain"
        return "html" if raw_prompt_type == "text/html" else "text"

    def _parse_response_data(self, resource_root: cc_xml.AssignmentElement) -> dict:
        """
        Parse response-related data.
        """
        accepted_format_types = self._parse_accepted_format_types(resource_root)
        is_file_submission_allowed = self._is_file_submission_allowed(accepted_format_types)
        is_textual_submission_allowed = self._is_textual_submission_allowed(accepted_format_types)
        file_upload_response = self._get_file_upload_response(is_textual_submission_allowed, is_file_submission_allowed)

        return {
            "text_response": self._get_text_response(is_textual_submission_allowed, is_file_submission_allowed),
            "text_response_editor": self._get_text_response_editor(accepted_format_types),
            "file_upload_response": file_upload_response,
            "allow_multiple_files": True,
            "file_upload_type": self._get_file_upload_type(file_upload_response),
            "white_listed_file_types": self._get_white_listed_file_types(file_upload_response),
        }

    def _parse_accepted_format_types(self, resource_root: cc_xml.AssignmentElement) -> Set[str]:
        """
        Parse accepted format types.
        """
        accepted_format_types = {accepted_format.attrib["type"] for accepted_format in resource_root.accepted_formats}
        return accepted_format_types or self.DEFAULT_ACCEPTED_FORMAT_TYPES

    @staticmethod
    def _is_file_submission_allowed(accepted_format_types: Set[str]) -> bool:
        """
        Decide whether submitting a file as an answer to assignment is allowed.
        """
        return AssignmentSubmissionFormatType.FILE in accepted_format_types

    @staticmethod
    def _is_textual_submission_allowed(accepted_format_types: Set[str]) -> bool:
        """
        Decide whether submitting a textual answer to assignment is allowed.
        """
        return bool(
            accepted_format_types.intersection(
                {
                    AssignmentSubmissionFormatType.HTML,
                    AssignmentSubmissionFormatType.TEXT,
                    AssignmentSubmissionFormatType.URL,
                }
            )
        )

    @staticmethod
    def _get_text_response(is_textual_submission_allowed: bool, is_file_submission_allowed: bool) -> str:
        """
        Provide text response necessity option.
        """
        if is_file_submission_allowed:
            return "optional" if is_textual_submission_allowed else ""
        return "required"

    @staticmethod
    def _get_file_upload_response(is_textual_submission_allowed: bool, is_file_submission_allowed: bool) -> str:
        """
        Provide file response necessity option.
        """
        if is_file_submission_allowed:
            return "optional" if is_textual_submission_allowed else "required"
        return ""

    @staticmethod
    def _get_text_response_editor(accepted_format_types: Set[str]) -> str:
        """
        Provide text response editor type.
        """
        return "tinymce" if AssignmentSubmissionFormatType.HTML in accepted_format_types else "text"

    def _get_file_upload_type(self, file_upload_response: str) -> Optional[str]:
        """
        Provide file upload type.
        """
        return self.DEFAULT_FILE_UPLOAD_TYPE if file_upload_response else None

    def _get_white_listed_file_types(self, file_upload_response: str) -> List[str]:
        """
        Provide file types allowed to submit.
        """
        return self.DEFAULT_WHITE_LISTED_FILE_TYPES if file_upload_response else []

    def _create_nodes(self, content: dict) -> List[xml.dom.minidom.Element]:
        """
        Give out <openassessment> OLX nodes.
        """
        doc = xml.dom.minidom.Document()
        el = element_builder(doc)

        ora = el(
            "openassessment",
            [
                el("title", content["title"]),
                el("assessments", [el("assessment", None, {"name": "staff-assessment", "required": "True"})]),
                el("prompts", [el("prompt", [el("description", content["prompt"])])]),
                el(
                    "rubric",
                    [
                        *generate_default_ora_criteria(),
                        el(
                            "feedbackprompt",
                            "(Optional) What aspects of this response stood out to you? What did it do well? How could "
                            "it be improved?",
                        ),
                        el("feedback_default_text", "I think that this response..."),
                    ],
                ),
            ],
            self._generate_openassessment_attributes(content),
        )

        return [ora]

    @staticmethod
    def _generate_openassessment_attributes(content: dict) -> Dict[str, str]:
        """
        Generate ORA root tag attributes.
        """
        attributes = {
            "prompts_type": content["prompts_type"],
            "text_response_editor": content["text_response_editor"],
            "text_response": content["text_response"],
            "file_upload_response": content["file_upload_response"],
            "allow_multiple_files": str(content["allow_multiple_files"]),
        }

        if content["file_upload_type"] is not None:
            attributes["file_upload_type"] = content["file_upload_type"]

        if content["white_listed_file_types"]:
            attributes["white_listed_file_types"] = ",".join(content["white_listed_file_types"])

        return attributes
