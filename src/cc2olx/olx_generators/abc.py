import xml.dom.minidom
from abc import ABC, abstractmethod
from typing import List, Union

from cc2olx.dataclasses import OlxGeneratorContext


class AbstractOlxGenerator(ABC):
    """
    Abstract base class for OLX generation for Common Cartridge content.
    """

    def __init__(self, context: OlxGeneratorContext) -> None:
        self._doc = xml.dom.minidom.Document()
        self._context = context

    @abstractmethod
    def create_nodes(self, content: Union[dict, List[dict]]) -> List[xml.dom.minidom.Element]:
        """
        Create OLX nodes.
        """
