import xml.dom.minidom
from unittest.mock import patch

import lxml

from cc2olx.dataclasses import OlxGeneratorContext
from cc2olx.iframe_link_parser import KalturaIframeLinkParser
from cc2olx.olx_generators import HtmlOlxGenerator


class TestHtmlOlxGenerator:
    def test_process_html_for_iframe_provides_video_blocks(self, iframe_content, link_map_csv):
        context = OlxGeneratorContext(iframe_link_parser=KalturaIframeLinkParser(link_map_csv), lti_consumer_ids=set())
        generator = HtmlOlxGenerator(context)

        _, video_olx = generator._process_html_for_iframe(iframe_content)

        assert len(video_olx) == 1
        assert video_olx[0].nodeName == "video"

    def test_process_html_for_iframe_removes_iframes_from_html(self, iframe_content, link_map_csv):
        context = OlxGeneratorContext(iframe_link_parser=KalturaIframeLinkParser(link_map_csv), lti_consumer_ids=set())
        generator = HtmlOlxGenerator(context)

        html_str, _ = generator._process_html_for_iframe(iframe_content)

        html = lxml.html.fromstring(html_str)
        iframe = html.xpath("//iframe")
        assert len(iframe) == 0

    def test_html_cleaning_from_cdata(self, cdata_containing_html, expected_cleaned_cdata_containing_html):
        """
        Test that CDATA cleaning function is called during HTML processing.

        Args:
            cdata_containing_html (str): HTML that contains CDATA tags.
            expected_cleaned_cdata_containing_html (str): Expected HTML after
                successful cleaning.
        """
        context = OlxGeneratorContext(iframe_link_parser=None, lti_consumer_ids=set())
        generator = HtmlOlxGenerator(context)
        content = {"html": cdata_containing_html}

        with patch(
            "cc2olx.olx_generators.html.clean_from_cdata",
            return_value=expected_cleaned_cdata_containing_html,
        ) as clean_from_cdata_mock:
            generator.create_nodes(content)

            clean_from_cdata_mock.assert_called_once()

    def test_processed_html_content_is_wrapped_into_cdata(self, cdata_containing_html):
        """
        Test that processed HTML content is wrapped into CDATA section.

        Args:
            cdata_containing_html (str): HTML that contains CDATA tags.
        """
        context = OlxGeneratorContext(iframe_link_parser=None, lti_consumer_ids=set())
        generator = HtmlOlxGenerator(context)
        content = {"html": cdata_containing_html}

        result_html, *__ = generator.create_nodes(content)

        assert isinstance(result_html.childNodes[0], xml.dom.minidom.CDATASection)
