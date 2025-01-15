import xml.dom.minidom
from abc import ABC, abstractmethod
from typing import List, Optional

from cc2olx.content_processors.dataclasses import ContentProcessorContext
from cc2olx.models import Cartridge


class AbstractContentProcessor(ABC):
    """
    Abstract base class for Common Cartridge content processing.

    To allow to process a specific Common Cartridge resource type, you need to
    create a subclass and implement a `process` method. To include the subclass
    into the processing workflow, you need to add it to the `CONTENT_PROCESSORS`
    setting.

    Sometimes it is needed to update the object outside the content processor
    during its execution. The allowed side effects are defined by the context
    interface. It is forbidden to mutate the cartridge object.
    """

    def __init__(self, cartridge: Cartridge, context: ContentProcessorContext) -> None:
        self._cartridge = cartridge
        self._context = context

    @abstractmethod
    def process(self, resource: dict, idref: str) -> Optional[List[xml.dom.minidom.Element]]:
        """
        Process a Common Cartridge resource content.

        Build the OLX nodes corresponding to the Common Cartridge resource.
        Some CC resources don't correspond to a single OLX node, so the list
        of nodes must be returned. For example, if a single QTI contains
        several items, it will be converted into a list of separate problem
        nodes.
        If the resource can not be processed, return `None`.
        """
