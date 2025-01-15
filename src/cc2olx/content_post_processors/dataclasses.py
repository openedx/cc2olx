from typing import Optional

import attrs


@attrs.define(frozen=True, slots=False)
class ContentPostProcessorContext:
    """
    Encapsulate a content post processor context.
    """

    relative_links_source: Optional[str]
