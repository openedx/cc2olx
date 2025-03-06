import json
import xml.dom.minidom

from cc2olx import olx
from .utils import format_xml


def test_olx_export_xml(
    cartridge,
    link_map_csv,
    studio_course_xml,
    relative_links_source,
    content_types_with_custom_blocks,
):
    xml = olx.OlxExport(
        cartridge,
        link_map_csv,
        relative_links_source=relative_links_source,
        content_types_with_custom_blocks=content_types_with_custom_blocks,
    ).xml()

    assert format_xml(xml) == format_xml(studio_course_xml)


def test_olx_export_wiki_page_disabled(cartridge, link_map_csv, studio_course_xml):
    policy_json = olx.OlxExport(cartridge, link_map_csv).policy()
    policy = json.loads(policy_json)
    tabs = policy["course/course"]["tabs"]

    for tab in tabs:
        if tab["name"] == "Wiki":
            assert tab["is_hidden"]


def test_fallback_nodes_are_created_for_element_without_identifierref(cartridge):
    element_data = {"identifier": "qti_1_6", "title": "Module 7 exam"}
    olx_export = olx.OlxExport(cartridge)
    olx_export.doc = xml.dom.minidom.Document()

    nodes = olx_export._create_olx_nodes(element_data)

    assert len(nodes) == 1
    assert nodes[0].toxml() == "<html><![CDATA[<p>MISSING CONTENT</p>]]></html>"


def test_fallback_nodes_are_created_for_element_with_missing_resource(cartridge):
    element_data = {"identifier": "qti_1_6", "identifierref": "not_existed_qti", "title": "Module 7 exam"}
    olx_export = olx.OlxExport(cartridge)
    olx_export.doc = xml.dom.minidom.Document()

    nodes = olx_export._create_olx_nodes(element_data)

    assert len(nodes) == 1
    assert nodes[0].toxml() == "<html><![CDATA[<p>MISSING CONTENT</p>]]></html>"


class TestOlxExporterLtiPolicy:
    def _get_oxl_exporter(self, cartridge, passports_csv, content_types_with_custom_blocks):
        """
        Helper function to create olx exporter.

        Args:
            cartridge ([Cartridge]): Cartridge class instance.
            link_map_csv ([str]): Csv file path.

        Returns:
            [OlxExport]: OlxExport instance.
        """
        olx_exporter = olx.OlxExport(
            cartridge,
            passport_file=passports_csv,
            content_types_with_custom_blocks=content_types_with_custom_blocks,
        )
        olx_exporter.doc = xml.dom.minidom.Document()
        return olx_exporter

    def test_lti_consumer_ids_are_defined(self, cartridge, passports_csv, content_types_with_custom_blocks):
        olx_exporter = self._get_oxl_exporter(cartridge, passports_csv, content_types_with_custom_blocks)
        _ = olx_exporter.xml()

        assert olx_exporter.lti_consumer_ids == {"external_tool_lti", "learning_tools_interoperability", "smart_quiz"}

    def test_policy_contains_advanced_module(self, cartridge, passports_csv, content_types_with_custom_blocks, caplog):
        olx_exporter = self._get_oxl_exporter(cartridge, passports_csv, content_types_with_custom_blocks)
        _ = olx_exporter.xml()
        caplog.clear()
        policy = json.loads(olx_exporter.policy())

        assert policy["course/course"]["advanced_modules"] == ["lti_consumer", *content_types_with_custom_blocks]
        # Converting to set because the order might change
        assert set(policy["course/course"]["lti_passports"]) == {
            "codio:my_codio_key:my_codio_secret",
            "lti_tool:my_consumer_key:my_consumer_secret_key",
            "external_tool_lti:external_tool_lti_key:external_tool_lti_secret",
            "learning_tools_interoperability:consumer_key:consumer_secret",
            "smart_quiz:smart_quiz_key:smart_quiz_secret",
        }

        # Warning for missing LTI passort is logged
        assert ["Missing LTI Passport for learning_tools_interoperability. Using default."] == [
            rec.message for rec in caplog.records
        ]
