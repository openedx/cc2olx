from collections import defaultdict
from typing import Dict, List, Optional, Type, TypeVar

from lxml import etree


QTI_NAMESPACE = "http://www.imsglobal.org/xsd/ims_qtiasiv1p2"


class CommonCartridgeElementBase(etree.ElementBase):
    """
    Base Common Cartridge XML element.
    """

    NODE_NAMESPACES: List[str]
    NODE_NAME: str


class CommonCartridgeElementClassLookup(etree.CustomElementClassLookup):
    """
    The lookup class for Common Cartridge XML elements.
    """

    _element_classes = defaultdict(dict)

    def lookup(
        self,
        node_type: str,
        document: etree._Document,
        namespace: Optional[dict],
        name: Optional[str],
    ) -> Optional[Type[CommonCartridgeElementBase]]:
        if node_type == "element":
            return self._element_classes.get(namespace, {}).get(name.lower(), CommonCartridgeElementBase)
        return None


CommonCartridgeElementType = TypeVar("CommonCartridgeElementType", bound=CommonCartridgeElementBase)


def common_cartridge_element(cls: CommonCartridgeElementType) -> CommonCartridgeElementType:
    """
    Add a type to the Common Cartridge XML lookup.
    """
    for namespace in cls.NODE_NAMESPACES:
        CommonCartridgeElementClassLookup._element_classes[namespace][cls.NODE_NAME] = cls

    return cls


@common_cartridge_element
class WebLink(CommonCartridgeElementBase):
    """
    Represent <webLink> Common Cartridge element.
    """

    SEARCH_NAMESPACE_OPTIONS = {
        "imswl_xmlv1p1": "http://www.imsglobal.org/xsd/imsccv1p1/imswl_v1p1",
        "imswl_xmlv1p2": "http://www.imsglobal.org/xsd/imsccv1p2/imswl_v1p2",
        "imswl_xmlv1p3": "http://www.imsglobal.org/xsd/imsccv1p3/imswl_v1p3",
    }
    NODE_NAMESPACES = list(SEARCH_NAMESPACE_OPTIONS.values())
    NODE_NAME = "weblink"

    def get_title(self, resource_type: str) -> CommonCartridgeElementBase:
        """
        Provide <title> child tag.
        """
        return self.find("wl:title", self._define_search_namespace(resource_type))

    def get_url(self, resource_type: str) -> CommonCartridgeElementBase:
        """
        Provide <url> child tag.
        """
        return self.find("wl:url", self._define_search_namespace(resource_type))

    def _define_search_namespace(self, resource_type: str) -> Dict[str, str]:
        """
        Define a search namespace based on resource type.
        """
        return {"wl": self.SEARCH_NAMESPACE_OPTIONS.get(resource_type)}


@common_cartridge_element
class BasicLtiLink(CommonCartridgeElementBase):
    """
    Represent <cartridge_basiclti_link> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {
        "blti": "http://www.imsglobal.org/xsd/imsbasiclti_v1p0",
        "lticp": "http://www.imsglobal.org/xsd/imslticp_v1p0",
        "lticm": "http://www.imsglobal.org/xsd/imslticm_v1p0",
    }
    NODE_NAMESPACES = [
        "http://www.imsglobal.org/xsd/imslticc_v1p0",
        "http://www.imsglobal.org/xsd/imslticc_v1p3",
    ]
    NODE_NAME = "cartridge_basiclti_link"

    @property
    def title(self) -> CommonCartridgeElementBase:
        """
        Provide <title> child tag.
        """
        return self.find("blti:title", self.SEARCH_NAMESPACES)

    @property
    def description(self) -> CommonCartridgeElementBase:
        """
        Provide <description> child tag.
        """
        return self.find("blti:description", self.SEARCH_NAMESPACES)

    @property
    def secure_launch_url(self) -> Optional[CommonCartridgeElementBase]:
        """
        Provide <secure_launch_url> child tag.
        """
        return self.find("blti:secure_launch_url", self.SEARCH_NAMESPACES)

    @property
    def launch_url(self) -> Optional[CommonCartridgeElementBase]:
        """
        Provide <launch_url> child tag.
        """
        return self.find("blti:launch_url", self.SEARCH_NAMESPACES)

    @property
    def width(self) -> Optional[CommonCartridgeElementBase]:
        """
        Provide width property descendant tag.
        """
        return self.find("blti:extensions/lticm:property[@name='selection_width']", self.SEARCH_NAMESPACES)

    @property
    def height(self) -> Optional[CommonCartridgeElementBase]:
        """
        Provide height property descendant tag.
        """
        return self.find("blti:extensions/lticm:property[@name='selection_height']", self.SEARCH_NAMESPACES)

    @property
    def custom(self) -> Optional[CommonCartridgeElementBase]:
        """
        Provide <custom> child tag.
        """
        return self.find("blti:custom", self.SEARCH_NAMESPACES)

    @property
    def canvas_tool_id(self) -> Optional[CommonCartridgeElementBase]:
        """
        Provide Canvas tool identifier property descendant tag.
        """
        return self.find("blti:extensions/lticm:property[@name='tool_id']", self.SEARCH_NAMESPACES)


@common_cartridge_element
class DiscussionTopic(CommonCartridgeElementBase):
    """
    Represent discussion <topic> Common Cartridge element.
    """

    SEARCH_NAMESPACE_OPTIONS = {
        "imsdt_xmlv1p1": "http://www.imsglobal.org/xsd/imsccv1p1/imsdt_v1p1",
        "imsdt_xmlv1p2": "http://www.imsglobal.org/xsd/imsccv1p2/imsdt_v1p2",
        "imsdt_xmlv1p3": "http://www.imsglobal.org/xsd/imsccv1p3/imsdt_v1p3",
    }
    NODE_NAMESPACES = list(SEARCH_NAMESPACE_OPTIONS.values())
    NODE_NAME = "topic"

    def get_title(self, resource_type: str) -> CommonCartridgeElementBase:
        """
        Provide <title> child tag.
        """
        return self.find("dt:title", self._define_search_namespace(resource_type))

    def get_text(self, resource_type: str) -> CommonCartridgeElementBase:
        """
        Provide <text> child tag.
        """
        return self.find("dt:text", self._define_search_namespace(resource_type))

    def _define_search_namespace(self, resource_type: str) -> Dict[str, str]:
        """
        Define a search namespace based on resource type.
        """
        return {"dt": self.SEARCH_NAMESPACE_OPTIONS.get(resource_type)}


@common_cartridge_element
class QtiElement(CommonCartridgeElementBase):
    """
    Represent <questestinterop> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "questestinterop"

    @property
    def items(self) -> List["QtiItem"]:
        """
        Provide <item> child tags.
        """
        return self.findall(".//qti:section/qti:item", self.SEARCH_NAMESPACES)


@common_cartridge_element
class QtiItem(CommonCartridgeElementBase):
    """
    Represent QTI <item> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "item"

    @property
    def presentation(self) -> "QtiPresentation":
        """
        Provide <presentation> child tag.
        """
        return self.find("qti:presentation", self.SEARCH_NAMESPACES)

    @property
    def description(self) -> str:
        """
        Provide <mattext> descendant tag.
        """
        return self.presentation.mattext.text

    @property
    def resprocessing(self) -> "QtiResprocessing":
        """
        Provide <resprocessing> child tag.
        """
        return self.find("qti:resprocessing", self.SEARCH_NAMESPACES)

    @property
    def qtimetadatafields(self) -> List["QtiMetadataField"]:
        """
        Provide <qtimetadatafield> descendant tag.
        """
        return self.findall("qti:itemmetadata/qti:qtimetadata/qti:qtimetadatafield", self.SEARCH_NAMESPACES)

    @property
    def profile(self) -> str:
        """
        Provide ``cc_profile`` value from problem metadata.

        This field is mandatory for problem, so the exception is thrown if
        it's not present.

        Example of metadata structure:
        ```
        <itemmetadata>
          <qtimetadata>
            <qtimetadatafield>
              <fieldlabel>cc_profile</fieldlabel>
              <fieldentry>cc.true_false.v0p1</fieldentry>
            </qtimetadatafield>
          </qtimetadata>
        </itemmetadata>
        ```
        """
        for field in self.qtimetadatafields:
            label = field.fieldlabel.text
            entry = field.fieldentry.text

            if label == "cc_profile":
                return entry

        raise ValueError('QTI metadata must contain "cc_profile" field.')

    @property
    def solution(self) -> Optional["QtiSolution"]:
        """
        Provide <solution> descendant tag.
        """
        return self.find("qti:itemfeedback/qti:solution", self.SEARCH_NAMESPACES)

    def get_itemfeedback(self, response_type: Optional[str] = None) -> Optional["QtiItemFeedback"]:
        """
        Provide <itemfeedback> child tag.
        """
        selector = "qti:itemfeedback"
        if response_type:
            selector = f"{selector}[@ident='{response_type}']"
        return self.find(selector, self.SEARCH_NAMESPACES)


@common_cartridge_element
class QtiMetadataField(CommonCartridgeElementBase):
    """
    Represent QTI <qtimetadatafield> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "qtimetadatafield"

    @property
    def fieldlabel(self) -> CommonCartridgeElementBase:
        """
        Provide <fieldlabel> child tag.
        """
        return self.find("qti:fieldlabel", self.SEARCH_NAMESPACES)

    @property
    def fieldentry(self) -> CommonCartridgeElementBase:
        """
        Provide <fieldentry> child tag.
        """
        return self.find("qti:fieldentry", self.SEARCH_NAMESPACES)


@common_cartridge_element
class QtiPresentation(CommonCartridgeElementBase):
    """
    Represent QTI <presentation> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "presentation"

    @property
    def response_labels(self) -> List["QtiResponseLabel"]:
        """
        Provide <response_label> descendant tags.
        """
        return self.findall("qti:response_lid/qti:render_choice/qti:response_label", self.SEARCH_NAMESPACES)

    @property
    def mattext(self) -> CommonCartridgeElementBase:
        """
        Provide <mattext> descendant tag.
        """
        return self.find("qti:material/qti:mattext", self.SEARCH_NAMESPACES)


@common_cartridge_element
class QtiResponseLabel(CommonCartridgeElementBase):
    """
    Represent QTI <response_label> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "response_label"

    @property
    def mattext(self) -> CommonCartridgeElementBase:
        """
        Provide <mattext> descendant tag.
        """
        return self.find("qti:material/qti:mattext", self.SEARCH_NAMESPACES)


@common_cartridge_element
class QtiResprocessing(CommonCartridgeElementBase):
    """
    Represent QTI <resprocessing> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "resprocessing"

    @property
    def respconditions(self) -> List["QtiRespcondition"]:
        """
        Provide <respcondition> descendant tags.
        """
        return self.findall("qti:respcondition", self.SEARCH_NAMESPACES)


@common_cartridge_element
class QtiRespcondition(CommonCartridgeElementBase):
    """
    Represent QTI <respcondition> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "respcondition"

    @property
    def varequals(self) -> List[CommonCartridgeElementBase]:
        """
        Provide <varequal> descendant tags.
        """
        return self.findall("qti:conditionvar/qti:varequal", self.SEARCH_NAMESPACES)

    @property
    def and_varequals(self) -> List[CommonCartridgeElementBase]:
        """
        Provide <varequal> descendant tags wrapped by <and> tag.
        """
        return self.findall("qti:conditionvar/qti:and/qti:varequal", self.SEARCH_NAMESPACES)

    @property
    def or_varequals(self) -> List[CommonCartridgeElementBase]:
        """
        Provide <varequal> descendant tags wrapped by <or> tag.
        """
        return self.findall("qti:conditionvar/qti:or/qti:varequal", self.SEARCH_NAMESPACES)

    @property
    def varsubstrings(self) -> List[CommonCartridgeElementBase]:
        """
        Provide <varsubstring> descendant tags.
        """
        return self.findall("qti:conditionvar/qti:varsubstring", self.SEARCH_NAMESPACES)

    def get_display_feedback(self, response_type: str) -> Optional[CommonCartridgeElementBase]:
        """
        Provide <displayfeedback> child tag.
        """
        return self.find(f"qti:displayfeedback[@linkrefid='{response_type}']", self.SEARCH_NAMESPACES)


@common_cartridge_element
class QtiSolution(CommonCartridgeElementBase):
    """
    Represent QTI <solution> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "solution"

    @property
    def mattext(self) -> CommonCartridgeElementBase:
        """
        Provide <mattext> descendant tag.
        """
        return self.find("qti:solutionmaterial//qti:material//qti:mattext", self.SEARCH_NAMESPACES)


@common_cartridge_element
class QtiItemFeedback(CommonCartridgeElementBase):
    """
    Represent QTI <itemfeedback> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "itemfeedback"

    @property
    def flow_mat(self) -> "QtiFlowMat":
        """
        Provide <flow_mat> child tag.
        """
        return self.find("qti:flow_mat", self.SEARCH_NAMESPACES)


@common_cartridge_element
class QtiFlowMat(CommonCartridgeElementBase):
    """
    Represent QTI <flow_mat> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "flow_mat"

    @property
    def material(self) -> "QtiMaterial":
        """
        Provide <material> child tag.
        """
        return self.find("qti:material", self.SEARCH_NAMESPACES)


@common_cartridge_element
class QtiMaterial(CommonCartridgeElementBase):
    """
    Represent QTI <material> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"qti": QTI_NAMESPACE}
    NODE_NAMESPACES = [QTI_NAMESPACE]
    NODE_NAME = "material"

    @property
    def mattext(self) -> CommonCartridgeElementBase:
        """
        Provide <mattext> child tag.
        """
        return self.find("qti:mattext", self.SEARCH_NAMESPACES)


class CommonCartridgeXmlParser(etree.XMLParser):
    """
    An XML parser configured to return Common Cartridge element objects.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_element_class_lookup(CommonCartridgeElementClassLookup())


@common_cartridge_element
class AssignmentElement(CommonCartridgeElementBase):
    """
    Represent <assignment> Common Cartridge element.
    """

    SEARCH_NAMESPACES = {"xsi": "http://www.imsglobal.org/xsd/imscc_extensions/assignment"}
    NODE_NAMESPACES = list(SEARCH_NAMESPACES.values())
    NODE_NAME = "assignment"

    @property
    def title(self) -> CommonCartridgeElementBase:
        """
        Provide <title> child tag.
        """
        return self.find("xsi:title", self.SEARCH_NAMESPACES)

    def get_text(self) -> Optional[CommonCartridgeElementBase]:
        """
        Provide <text> child tag.
        """
        return self.find("xsi:text", self.SEARCH_NAMESPACES)

    @property
    def instructor_text(self) -> CommonCartridgeElementBase:
        """
        Provide <instructor_text> child tag.
        """
        return self.find("xsi:instructor_text", self.SEARCH_NAMESPACES)

    @property
    def accepted_formats(self) -> List[CommonCartridgeElementBase]:
        """
        Provide <format> children of <submission_formats> child tag.
        """
        return self.findall("xsi:submission_formats/xsi:format", self.SEARCH_NAMESPACES)
