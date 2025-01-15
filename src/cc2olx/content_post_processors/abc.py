import xml.dom.minidom
from abc import ABC, abstractmethod

from cc2olx.content_post_processors.dataclasses import ContentPostProcessorContext
from cc2olx.models import Cartridge


class AbstractContentPostProcessor(ABC):
    """
    Abstract base class for content post-processing.

    To encapsulate generated OLX node modification logic, you need to create a
    subclass and implement a `process` method. To include the subclass into the
    post-processing workflow, you need to add it to the `CONTENT_POST_PROCESSORS`
    setting.
    """

    def __init__(self, cartridge: Cartridge, context: ContentPostProcessorContext) -> None:
        self._cartridge = cartridge
        self._context = context

    @abstractmethod
    def process(self, element: xml.dom.minidom.Element) -> None:
        """
        Perform post-processing logic by modifying the element and its children.
        """
