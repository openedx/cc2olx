from cc2olx import olx
from .utils import format_xml
import xml.dom.minidom
import lxml


def test_olx_export(cartridge, studio_course_xml):
    xml = olx.OlxExport(cartridge).xml()

    assert format_xml(xml) == format_xml(studio_course_xml)


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
        nodes = olx_exporter._create_olx_nodes('html', {"html": iframe_content})
        # Html xblock and video xblock
        assert len(nodes) == 2
