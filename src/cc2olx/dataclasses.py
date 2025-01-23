from dataclasses import dataclass, field
from collections import ChainMap
from typing import Callable, Dict, List, NamedTuple, Optional, Set

import attrs

from cc2olx.iframe_link_parser import IframeLinkParser


@dataclass
class OlxToOriginalStaticFilePaths:
    """
    Provide OLX static file to Common cartridge static file mappings.
    """

    # Static files from `web_resources` directory
    web_resources: Dict[str, str] = field(default_factory=dict)
    # Static files that are outside of `web_resources` directory, but still required
    extra: Dict[str, str] = field(default_factory=dict)

    def add_web_resource_path(self, olx_static_path: str, cc_static_path: str) -> None:
        """
        Add web resource static file mapping.
        """
        self.web_resources[olx_static_path] = cc_static_path

    def add_extra_path(self, olx_static_path: str, cc_static_path: str) -> None:
        """
        Add extra static file mapping.
        """
        self.extra[olx_static_path] = cc_static_path

    def __post_init__(self) -> None:
        self.all = ChainMap(self.extra, self.web_resources)


class LinkKeywordProcessor(NamedTuple):
    """
    Encapsulate a link keyword and it's processor.
    """

    keyword: str
    processor: Callable[[str, str], str]


class FibProblemRawAnswers(NamedTuple):
    """
    Encapsulate answers data for a Fill-In-The-Blank problem.
    """

    exact_answers: List[str]
    answer_patterns: List[str]


@attrs.define(frozen=True, slots=False)
class OlxGeneratorContextMixin:
    """
    Encapsulate an OLX generator context data.
    """

    iframe_link_parser: Optional[IframeLinkParser]
    _lti_consumer_ids: Set[str]

    def add_lti_consumer_id(self, lti_consumer_id: str) -> None:
        """
        Populate LTI consumer IDs set with a provided value.
        """
        self._lti_consumer_ids.add(lti_consumer_id)


class OlxGeneratorContext(OlxGeneratorContextMixin):
    """
    Encapsulate an OLX generator context.

    Provide additional initialization methods.
    """

    @classmethod
    def from_content_processor_context(
        cls,
        content_processor_context: "ContentProcessorContext",
    ) -> "OlxGeneratorContext":
        """
        Create the OLX generator context from the content processor context.
        """
        return cls(
            iframe_link_parser=content_processor_context.iframe_link_parser,
            lti_consumer_ids=content_processor_context._lti_consumer_ids,
        )


@attrs.define(frozen=True, slots=False)
class ContentParserContextMixin:
    """
    Encapsulate a content parser context data.
    """

    relative_links_source: Optional[str]


class ContentParserContext(ContentParserContextMixin):
    """
    Encapsulate a content parser context.

    Provide additional initialization methods.
    """

    @classmethod
    def from_content_processor_context(
        cls,
        content_processor_context: "ContentProcessorContext",
    ) -> "ContentParserContext":
        """
        Create the content parser context from the content processor context.
        """
        return cls(content_processor_context.relative_links_source)


@attrs.define(frozen=True, slots=False)
class ContentProcessorContext(ContentParserContextMixin, OlxGeneratorContextMixin):
    """
    Encapsulate a content processor context.
    """
