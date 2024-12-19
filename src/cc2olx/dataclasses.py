from dataclasses import dataclass, field
from collections import ChainMap
from typing import Dict


@dataclass
class OlxToOriginalStaticFilePaths:
    """
    Provide OLX static file to Common cartridge static file mappings.
    """

    # Static files from `web_resources` directory
    web_resources: Dict[str, str] = field(default_factory=dict)
    # Static files that are outside of `web_resources` directory, but still required
    extra: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.all = ChainMap(self.extra, self.web_resources)
