from unittest.mock import Mock, patch

from cc2olx.content_parsers import VideoContentParser


class TestVideoContentParser:
    def test_parse_content_returns_none_if_there_is_no_resource_identifier(self):
        parser = VideoContentParser(Mock(), Mock())

        actual_content = parser._parse_content(None)

        assert actual_content is None

    @patch(
        "cc2olx.content_parsers.video.VideoContentParser._parse_web_link_content",
        Mock(return_value={"href": "youtube.com/watch?v=ABCDeF12345"}),
    )
    def test_parse_content_parses_youtube_link(self):
        parser = VideoContentParser(Mock(), Mock())
        expected_content = {"youtube": "ABCDeF12345"}

        actual_content = parser._parse_content(Mock())

        assert actual_content == expected_content
