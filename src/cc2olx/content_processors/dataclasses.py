from typing import Optional, Set

import attrs

from cc2olx.iframe_link_parser import IframeLinkParser


@attrs.define(frozen=True, slots=False)
class ContentProcessorContext:
    """
    Encapsulate a content processor context.
    """

    iframe_link_parser: Optional[IframeLinkParser]
    _lti_consumer_ids: Set[str]

    def add_lti_consumer_id(self, lti_consumer_id: str) -> None:
        """
        Populate LTI consumer IDs set with a provided value.
        """
        self._lti_consumer_ids.add(lti_consumer_id)
