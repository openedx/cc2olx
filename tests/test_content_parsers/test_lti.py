from unittest.mock import Mock

from cc2olx.content_parsers import LtiContentParser


class TestLtiContentParser:
    def test_parsing_results(self, cartridge):
        parser = LtiContentParser(cartridge, Mock())

        assert parser.parse("resource_2_lti") == {
            "title": "Learning Tools Interoperability",
            "description": "https://www.imsglobal.org/activity/learning-tools-interoperability",
            "launch_url": "https://lti.local/launch",
            "height": "500",
            "width": "500",
            "custom_parameters": {},
            "lti_id": "learning_tools_interoperability",
        }
