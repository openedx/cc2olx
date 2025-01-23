import xml.dom.minidom
from typing import List

from cc2olx.olx_generators import AbstractOlxGenerator
from cc2olx.utils import element_builder


class LtiOlxGenerator(AbstractOlxGenerator):
    """
    Generate OLX for LTIs.
    """

    def create_nodes(self, content: dict) -> List[xml.dom.minidom.Element]:
        el = element_builder(self._doc)

        custom_parameters = "[{params}]".format(
            params=", ".join(
                [
                    '"{key}={value}"'.format(
                        key=key,
                        value=value,
                    )
                    for key, value in content["custom_parameters"].items()
                ]
            ),
        )
        lti_consumer_node = el(
            "lti_consumer",
            [],
            {
                "custom_parameters": custom_parameters,
                "description": content["description"],
                "display_name": content["title"],
                "inline_height": content["height"],
                "inline_width": content["width"],
                "launch_url": content["launch_url"],
                "modal_height": content["height"],
                "modal_width": content["width"],
                "xblock-family": "xblock.v1",
                "lti_id": content["lti_id"],
            },
        )
        return [lti_consumer_node]
