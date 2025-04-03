from typing import List, Optional, Set

import attrs

from cc2olx.iframe_link_parser import IframeLinkParser


@attrs.define(frozen=True, slots=False)
class ContentProcessorContext:
    """
    Encapsulate a content processor context.
    """

    iframe_link_parser: Optional[IframeLinkParser]
    _lti_consumer_ids: Set[str]
    _content_types_with_custom_blocks: List[str]

    def add_lti_consumer_id(self, lti_consumer_id: str) -> None:
        """
        Populate LTI consumer IDs set with a provided value.
        """
        self._lti_consumer_ids.add(lti_consumer_id)

    def is_content_type_with_custom_block_used(self, content_type: str) -> bool:
        """
        Decide whether a content type with custom block is used.
        """
        return content_type in self._content_types_with_custom_blocks
