import json
from unittest.mock import Mock

import lxml
import xml.dom.minidom

from cc2olx import olx

from .utils import format_xml


def test_olx_export_xml(cartridge, link_map_csv, studio_course_xml):
    xml = olx.OlxExport(cartridge, link_map_csv).xml()

    assert format_xml(xml) == format_xml(studio_course_xml)


def test_olx_export_wiki_page_disabled(cartridge, link_map_csv, studio_course_xml):
    policy_json = olx.OlxExport(cartridge, link_map_csv).policy()
    policy = json.loads(policy_json)
    tabs = policy["course/course"]["tabs"]

    for tab in tabs:
        if tab["name"] == "Wiki":
            assert tab["is_hidden"]


def test_process_link():
    details = {"href": "https://example.com/path"}
    details_with_youtube_link = {"href": "https://www.youtube.com/watch?v=gQ-cZRmHfs4&amp;amp;list=PL5B350D511278A56B"}

    assert olx.process_link(details) == (
        "html",
        {"html": "<a href='{}'></a>".format(details["href"])},
    )

    assert olx.process_link(details_with_youtube_link) == (
        "video",
        {"youtube": "gQ-cZRmHfs4"},
    )


class TestOlXExporeterHTMLProcessing:
    """
    Test the OLX exporter for HTML parsing flow.
    """

    def test_html_cleaning_from_cdata(
        self,
        mocker,
        bare_olx_exporter,
        cdata_containing_html,
        expected_cleaned_cdata_containing_html,
    ):
        """
        Test that CDATA cleaning function is called during HTML processing.

        Args:
            mocker (MockerFixture): MockerFixture instance.
            bare_olx_exporter (OlxExport): bare OLX exporter.
            cdata_containing_html (str): HTML that contains CDATA tags.
            expected_cleaned_cdata_containing_html (str): Expected HTML after
                successful cleaning.
        """
        details = {"html": cdata_containing_html}

        clean_from_cdata_mock = mocker.patch(
            "cc2olx.olx.clean_from_cdata",
            return_value=expected_cleaned_cdata_containing_html,
        )

        bare_olx_exporter._process_html(details)

        clean_from_cdata_mock.assert_called_once()

    def test_processed_html_content_is_wrapped_into_cdata(self, bare_olx_exporter, cdata_containing_html):
        """
        Test that processed HTML content is wrapped into CDATA section.

        Args:
            bare_olx_exporter (OlxExport): bare OLX exporter.
            cdata_containing_html (str): HTML that contains CDATA tags.
        """
        details = {"html": cdata_containing_html}

        result_html, *__ = bare_olx_exporter._process_html(details)

        assert isinstance(result_html.childNodes[0], xml.dom.minidom.CDATASection)


class TestOlXExporeterIframeParser:
    """
    Test the olx exporter for iframe link parsing flow
    """

    def _get_oxl_exporter(self, cartridge, link_map_csv):
        """
        Helper function to create olx exporter.

        Args:
            cartridge ([Cartridge]): Cartridge class instance.
            link_map_csv ([str]): Csv file path.

        Returns:
            [OlxExport]: OlxExport instance.
        """
        olx_exporter = olx.OlxExport(cartridge, link_file=link_map_csv)
        olx_exporter.doc = xml.dom.minidom.Document()
        return olx_exporter

    def test_process_html_for_iframe_video_blocks(self, cartridge, link_map_csv, iframe_content):
        """
        Test if the iframe is getting parsed and video blocks being generated.

        Args:
            cartridge ([Cartridge]): Cartridge class instance.
            link_map_csv ([str]): Csv file path.
            iframe_content ([str]): Html file content.
        """
        olx_exporter = self._get_oxl_exporter(cartridge, link_map_csv)
        _, video_olx = olx_exporter._process_html_for_iframe(iframe_content)
        assert len(video_olx) == 1

    def test_process_html_for_iframe_html_removed(self, cartridge, link_map_csv, iframe_content):
        """
        Test if iframe is removed from html.

        Args:
            cartridge ([Cartridge]): Cartridge class instance.
            link_map_csv ([str]): Csv file path.
            iframe_content ([str]): Html file content.
        """
        olx_exporter = self._get_oxl_exporter(cartridge, link_map_csv)
        html_str, _ = olx_exporter._process_html_for_iframe(iframe_content)
        html = lxml.html.fromstring(html_str)
        iframe = html.xpath("//iframe")
        assert len(iframe) == 0

    def test_create_olx_nodes(self, cartridge, link_map_csv, iframe_content):
        """
        Test create olx nodes with html content.

        Args:
            cartridge ([Cartridge]): Cartridge class instance.
            link_map_csv ([str]): Csv file path.
            iframe_content ([str]): Html file content.
        """
        olx_exporter = self._get_oxl_exporter(cartridge, link_map_csv)
        nodes = olx_exporter._create_olx_nodes("html", {"html": iframe_content})
        # Html xblock and video xblock
        assert len(nodes) == 2


class TestOlxExporterLtiPolicy:
    def _get_oxl_exporter(self, cartridge, passports_csv):
        """
        Helper function to create olx exporter.

        Args:
            cartridge ([Cartridge]): Cartridge class instance.
            link_map_csv ([str]): Csv file path.

        Returns:
            [OlxExport]: OlxExport instance.
        """
        olx_exporter = olx.OlxExport(cartridge, passport_file=passports_csv)
        olx_exporter.doc = xml.dom.minidom.Document()
        return olx_exporter

    def test_lti_consumer_present_set_to_true(self, cartridge, passports_csv):
        olx_exporter = self._get_oxl_exporter(cartridge, passports_csv)
        _ = olx_exporter.xml()

        assert olx_exporter.lti_consumer_present is True
        assert olx_exporter.lti_consumer_ids == {"external_tool_lti", "learning_tools_interoperability"}

    def test_policy_contains_advanced_module(self, cartridge, passports_csv, caplog):
        olx_exporter = self._get_oxl_exporter(cartridge, passports_csv)
        _ = olx_exporter.xml()
        caplog.clear()
        policy = json.loads(olx_exporter.policy())

        assert policy["course/course"]["advanced_modules"] == ["lti_consumer"]
        # Converting to set because the order might change
        assert set(policy["course/course"]["lti_passports"]) == {
            "codio:my_codio_key:my_codio_secret",
            "lti_tool:my_consumer_key:my_consumer_secret_key",
            "external_tool_lti:external_tool_lti_key:external_tool_lti_secret",
            "learning_tools_interoperability:consumer_key:consumer_secret",
        }

        # Warning for missing LTI passort is logged
        assert ["Missing LTI Passport for learning_tools_interoperability. Using default."] == [
            rec.message for rec in caplog.records
        ]


class TestDiscussionParsing:
    """
    Test the OLX exporter for discussion parsing flow.
    """

    def test_discussion_content_cleaning_from_cdata(
        self,
        mocker,
        bare_olx_exporter,
        cdata_containing_html,
        expected_cleaned_cdata_containing_html,
    ):
        """
        Test that CDATA cleaning function is called during discussion parsing.

        Args:
            mocker (MockerFixture): MockerFixture instance.
            bare_olx_exporter (OlxExport): bare OLX exporter.
            cdata_containing_html (str): HTML that contains CDATA tags.
            expected_cleaned_cdata_containing_html (str): Expected HTML after
                successful cleaning.
        """
        details = {"dependencies": [], "title": Mock(), "text": cdata_containing_html}

        clean_from_cdata_mock = mocker.patch(
            "cc2olx.olx.clean_from_cdata",
            return_value=expected_cleaned_cdata_containing_html,
        )

        bare_olx_exporter._create_discussion_node(details)

        clean_from_cdata_mock.assert_called_once()

    def test_discussion_decription_is_wrapped_into_cdata(self, bare_olx_exporter, cdata_containing_html):
        """
        Test that processed HTML content is wrapped into CDATA section.

        Args:
            bare_olx_exporter (OlxExport): bare OLX exporter.
            cdata_containing_html (str): HTML that contains CDATA tags.
        """
        details = {"dependencies": [], "title": Mock(), "text": cdata_containing_html}

        discussion_decription_html, __ = bare_olx_exporter._create_discussion_node(details)

        assert isinstance(discussion_decription_html.childNodes[0], xml.dom.minidom.CDATASection)
