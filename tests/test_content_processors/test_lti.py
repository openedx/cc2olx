from cc2olx.content_processors import LtiContentProcessor


class TestLtiContentProcessor:
    def test_parsing_results(self, cartridge, empty_content_processor_context):
        processor = LtiContentProcessor(cartridge, empty_content_processor_context)

        assert processor._parse(cartridge.define_resource("resource_2_lti"), "resource_2_lti") == {
            "title": "Learning Tools Interoperability",
            "description": "https://www.imsglobal.org/activity/learning-tools-interoperability",
            "launch_url": "https://lti.local/launch",
            "height": "500",
            "width": "500",
            "custom_parameters": {},
            "lti_id": "learning_tools_interoperability",
        }
