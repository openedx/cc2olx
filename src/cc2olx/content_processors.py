import xml.dom.minidom
from typing import List, Optional, Type, Union

from cc2olx import content_parsers, olx_generators
from cc2olx.dataclasses import ContentParserContext, ContentProcessorContext, OlxGeneratorContext
from cc2olx.models import Cartridge


class AbstractContentProcessor:
    """
    Abstract base class for Common Cartridge content processing.
    """

    content_parser_class: Type[content_parsers.AbstractContentParser]
    olx_generator_class: Type[olx_generators.AbstractOlxGenerator]

    def __init__(self, cartridge: Cartridge, context: ContentProcessorContext) -> None:
        self._cartridge = cartridge
        self._context = context

    def process(self, idref: Optional[str]) -> Optional[List[xml.dom.minidom.Element]]:
        """
        Process a Common Cartridge resource content.
        """
        parser = self.content_parser_class(
            self._cartridge,
            ContentParserContext.from_content_processor_context(self._context),
        )
        if content := parser.parse(idref):
            self._pre_olx_generation(content)
            olx_generator = self.olx_generator_class(OlxGeneratorContext.from_content_processor_context(self._context))
            return olx_generator.create_nodes(content)
        return None

    def _pre_olx_generation(self, content: Union[list, dict]) -> None:
        """
        The hook for actions performing before OLX generation.
        """


class HtmlContentProcessor(AbstractContentProcessor):
    """
    HTML content processor.
    """

    content_parser_class = content_parsers.HtmlContentParser
    olx_generator_class = olx_generators.HtmlOlxGenerator


class VideoContentProcessor(AbstractContentProcessor):
    """
    Video content processor.
    """

    content_parser_class = content_parsers.VideoContentParser
    olx_generator_class = olx_generators.VideoOlxGenerator


class LtiContentProcessor(AbstractContentProcessor):
    """
    LTI content processor.
    """

    content_parser_class = content_parsers.LtiContentParser
    olx_generator_class = olx_generators.LtiOlxGenerator

    def _pre_olx_generation(self, content: dict) -> None:
        """
        Populate LTI consumer IDs with the resource LTI ID.
        """
        self._context.add_lti_consumer_id(content["lti_id"])


class QtiContentProcessor(AbstractContentProcessor):
    """
    QTI content processor.
    """

    content_parser_class = content_parsers.QtiContentParser
    olx_generator_class = olx_generators.QtiOlxGenerator


class DiscussionContentProcessor(AbstractContentProcessor):
    """
    Discussion content processor.
    """

    content_parser_class = content_parsers.DiscussionContentParser
    olx_generator_class = olx_generators.DiscussionOlxGenerator
