from abc import ABC, abstractmethod
from typing import Optional, Union

from cc2olx.content_parsers.utils import StaticLinkProcessor
from cc2olx.dataclasses import ContentParserContext
from cc2olx.models import Cartridge


class AbstractContentParser(ABC):
    """
    Abstract base class for parsing Common Cartridge content.
    """

    def __init__(self, cartridge: Cartridge, context: ContentParserContext) -> None:
        self._cartridge = cartridge
        self._context = context

    def parse(self, idref: Optional[str]) -> Optional[Union[list, dict]]:
        """
        Parse the resource with the specified identifier.
        """
        if content := self._parse_content(idref):
            link_processor = StaticLinkProcessor(self._cartridge, self._context.relative_links_source)
            content = link_processor.process_content_static_links(content)
        return content

    @abstractmethod
    def _parse_content(self, idref: Optional[str]) -> Optional[Union[list, dict]]:
        """
        Parse content of the resource with the specified identifier.
        """
