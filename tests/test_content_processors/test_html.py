import pytest

from cc2olx.content_processors import HtmlContentProcessor
from cc2olx.models import Cartridge


class TestHtmlContentProcessor:
    def test_not_imported_content_without_link_processing(
        self,
        corner_cases_imscc,
        temp_workspace_path,
        empty_content_processor_context,
    ):
        cartridge = Cartridge(corner_cases_imscc, temp_workspace_path)
        cartridge.load_manifest_extracted()
        cartridge.normalize()
        processor = HtmlContentProcessor(cartridge, empty_content_processor_context)
        idref = "unknown_resource_without_link_content"
        resource = cartridge.define_resource(idref)

        olx_nodes = processor.process(resource, idref)

        assert len(olx_nodes) == 1
        assert olx_nodes[0].toxml() == "<html><![CDATA[Not imported content: type = 'imsunknwn_xmlv1p3']]></html>"

    def test_not_imported_content_with_link_processing(
        self,
        corner_cases_imscc,
        temp_workspace_path,
        empty_content_processor_context,
    ):
        cartridge = Cartridge(corner_cases_imscc, temp_workspace_path)
        cartridge.load_manifest_extracted()
        cartridge.normalize()
        processor = HtmlContentProcessor(cartridge, empty_content_processor_context)
        idref = "unknown_resource_with_link_content"
        resource = cartridge.define_resource(idref)

        olx_nodes = processor.process(resource, idref)

        assert len(olx_nodes) == 1
        assert olx_nodes[0].toxml() == (
            "<html><![CDATA[Not imported content: type = 'imsunknwn_xmlv1p3', href = "
            "'unknown_resources/res1.png']]></html>"
        )

    def test_exception_is_raised_if_webcontent_html_file_do_not_exist(
        self,
        corner_cases_imscc,
        temp_workspace_path,
        empty_content_processor_context,
    ):
        cartridge = Cartridge(corner_cases_imscc, temp_workspace_path)
        cartridge.load_manifest_extracted()
        cartridge.normalize()
        processor = HtmlContentProcessor(cartridge, empty_content_processor_context)
        idref = "migration_patterns_R"
        resource = cartridge.define_resource(idref)

        with pytest.raises(FileNotFoundError):
            processor.process(resource, idref)

    def test_not_supported_webcontent_processing(
        self,
        corner_cases_imscc,
        temp_workspace_path,
        empty_content_processor_context,
    ):
        cartridge = Cartridge(corner_cases_imscc, temp_workspace_path)
        cartridge.load_manifest_extracted()
        cartridge.normalize()
        processor = HtmlContentProcessor(cartridge, empty_content_processor_context)
        idref = "not_supported_webcontent_R"
        resource = cartridge.define_resource(idref)

        olx_nodes = processor.process(resource, idref)

        assert len(olx_nodes) == 1
        assert olx_nodes[0].toxml() == "<html><![CDATA[<p>MISSING CONTENT</p>]]></html>"

    def test_parsing_results(self, cartridge, empty_content_processor_context):
        processor = HtmlContentProcessor(cartridge, empty_content_processor_context)

        assert processor._parse(cartridge.define_resource("resource_1_course"), "resource_1_course") == {
            "html": "Not imported content: type = 'associatedcontent/imscc_xmlv1p1/learning-application-resource', "
            "href = 'course_settings/canvas_export.txt'"
        }

        assert processor._parse(cartridge.define_resource("resource_3_vertical"), "resource_3_vertical") == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_3_vertical"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<img src="%24IMS-CC-FILEBASE%24/QuizImages/fractal.jpg" alt="fractal.jpg"'
            ' width="500" height="375" />\n'
            "<p>Fractal Image <a "
            'href="%24IMS-CC-FILEBASE%24/QuizImages/fractal.jpg?canvas_download=1" '
            'target="_blank">Fractal Image</a></p>\n'
            "</body>\n</html>\n"
        }

        assert processor._parse(
            cartridge.define_resource("resource_6_wiki_content"),
            "resource_6_wiki_content",
        ) == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_6_wiki_content"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="%24WIKI_REFERENCE%24/pages/wiki_content">Wiki Content</a>'
            "\n</body>\n</html>\n"
        }

        assert processor._parse(
            cartridge.define_resource("resource_7_canvas_content"),
            "resource_7_canvas_content",
        ) == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_7_canvas_content"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="%24CANVAS_OBJECT_REFERENCE%24/quizzes/abc">Canvas Content</a>'
            "\n</body>\n</html>\n"
        }

        assert processor._parse(
            cartridge.define_resource("resource_module-|-introduction"),
            "resource_module-|-introduction",
        ) == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_module-|-introduction"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="%24WIKI_REFERENCE%24/pages/wiki_content">Wiki Content</a>'
            "\n</body>\n</html>\n"
        }

    @pytest.mark.parametrize(
        "resource_type",
        [
            "imsbasiclti_xmlv1p2",
            "imsbasiclti_xmlv1p3",
            "imsqti_xmlv1p3/imscc_xmlv1p1/assessment",
            "imsqti_xmlv1p3/imscc_xmlv1p3/assessment",
            "imsdt_xmlv1p2",
            "imsdt_xmlv1p3",
        ],
    )
    def test_known_unprocessed_resource_types_is_detected(
        self,
        resource_type,
        cartridge,
        empty_content_processor_context,
    ):
        processor = HtmlContentProcessor(cartridge, empty_content_processor_context)

        assert processor.is_known_unprocessed_resource_type(resource_type) is True

    @pytest.mark.parametrize("resource_type", ["imsbasicabc_xmlv1p2", "imsexample_xmlv1p3", "not_cc_type", "imsscorm"])
    def test_not_known_unprocessed_resource_types_is_detected(
        self,
        resource_type,
        cartridge,
        empty_content_processor_context,
    ):
        processor = HtmlContentProcessor(cartridge, empty_content_processor_context)

        assert processor.is_known_unprocessed_resource_type(resource_type) is False
