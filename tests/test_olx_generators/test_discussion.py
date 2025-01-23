import xml.dom.minidom
from unittest.mock import Mock, patch

from cc2olx.olx_generators import DiscussionOlxGenerator


class TestDiscussionOlxGenerator:
    def test_discussion_content_cleaning_from_cdata(
        self,
        cdata_containing_html,
        expected_cleaned_cdata_containing_html,
    ):
        """
        Test that CDATA cleaning function is called during discussion parsing.

        Args:
            cdata_containing_html (str): HTML that contains CDATA tags.
            expected_cleaned_cdata_containing_html (str): Expected HTML after
                successful cleaning.
        """
        generator = DiscussionOlxGenerator(Mock())
        content = {"dependencies": [], "title": Mock(), "text": cdata_containing_html}

        with patch(
            "cc2olx.olx_generators.discussion.clean_from_cdata",
            return_value=expected_cleaned_cdata_containing_html,
        ) as clean_from_cdata_mock:
            generator.create_nodes(content)

            clean_from_cdata_mock.assert_called_once()

    def test_discussion_description_is_wrapped_into_cdata(self, cdata_containing_html):
        """
        Test that processed HTML content is wrapped into CDATA section.

        Args:
            cdata_containing_html (str): HTML that contains CDATA tags.
        """
        generator = DiscussionOlxGenerator(Mock())
        content = {"dependencies": [], "title": Mock(), "text": cdata_containing_html}

        discussion_description_html, __ = generator.create_nodes(content)

        assert isinstance(discussion_description_html.childNodes[0], xml.dom.minidom.CDATASection)
