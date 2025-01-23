from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from cc2olx.content_parsers import HtmlContentParser


class TestHtmlContentParser:
    def test_parse_content_returns_default_content_if_there_is_no_resource_identifier(self):
        parser = HtmlContentParser(Mock(), Mock())
        expected_content = {"html": "<p>MISSING CONTENT</p>"}

        actual_content = parser._parse_content(None)

        assert actual_content == expected_content

    def test_parse_content_returns_default_content_if_the_resource_is_missed_in_cartridge(self):
        cartridge_mock = Mock(define_resource=Mock(return_value=None))
        parser = HtmlContentParser(cartridge_mock, Mock())
        expected_content = {"html": "<p>MISSING CONTENT</p>"}

        actual_content = parser._parse_content(Mock())

        assert actual_content == expected_content

    @patch("cc2olx.content_parsers.html.logger")
    def test_parse_content_logs_missing_resource(self, logger_mock):
        cartridge_mock = Mock(define_resource=Mock(return_value=None))
        parser = HtmlContentParser(cartridge_mock, Mock())
        idref_mock = Mock()

        parser._parse_content(idref_mock)

        logger_mock.info.assert_called_once_with("Missing resource: %s", idref_mock)

    @patch("cc2olx.content_parsers.html.HtmlContentParser._parse_web_link_content", Mock(return_value=None))
    @patch("cc2olx.content_parsers.html.HtmlContentParser.is_known_unprocessed_resource_type", Mock(return_value=True))
    def test_parse_content_returns_default_content_for_known_unprocessed_resource_types(self):
        parser = HtmlContentParser(MagicMock(), Mock())
        expected_content = {"html": "<p>MISSING CONTENT</p>"}

        actual_content = parser._parse_content(Mock())

        assert actual_content == expected_content

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
    def test_known_unprocessed_resource_types_is_detected(self, resource_type):
        parser = HtmlContentParser(Mock(), Mock())

        assert parser.is_known_unprocessed_resource_type(resource_type) is True

    @pytest.mark.parametrize("resource_type", ["imsbasicabc_xmlv1p2", "imsexample_xmlv1p3", "not_cc_type", "imsscorm"])
    def test_not_known_unprocessed_resource_types_is_detected(self, resource_type):
        parser = HtmlContentParser(Mock(), Mock())

        assert parser.is_known_unprocessed_resource_type(resource_type) is False

    @pytest.mark.parametrize(
        "resource_type",
        ["unsupported_resource_type", "chess_game_xmlv1p1", "drag_and_drop_xmlv1p1", "imsab_xmlv1p2"],
    )
    @patch("cc2olx.content_parsers.html.HtmlContentParser._parse_web_link_content", Mock(return_value=None))
    @patch("cc2olx.content_parsers.html.HtmlContentParser._parse_not_imported_content")
    def test_parse_content_parses_not_imported_content(self, parse_not_imported_content_mock, resource_type):
        cartridge_mock = Mock(define_resource=Mock(return_value={"type": "imsqti_xmlv1p2"}))
        parser = HtmlContentParser(cartridge_mock, Mock())

        actual_content = parser._parse_content(Mock())

        assert actual_content == parse_not_imported_content_mock.return_value

    @patch("cc2olx.content_parsers.html.imghdr.what", Mock(return_value=None))
    def test_parse_webcontent_returns_default_content_for_unknown_webcontent_type_from_web_resources_dir(self):
        parser = HtmlContentParser(
            Mock(build_resource_file_path=Mock(return_value=Path("web_resources/unknown/path/to/file.ext"))),
            Mock(),
        )
        expected_content = {"html": "<p>MISSING CONTENT</p>"}

        actual_content = parser._parse_webcontent(Mock(), MagicMock())

        assert actual_content == expected_content

    @patch("cc2olx.content_parsers.html.logger")
    @patch("cc2olx.content_parsers.html.imghdr.what", Mock(return_value=None))
    def test_parse_webcontent_logs_skipping_webcontent(self, logger_mock):
        resource_file_path = Path("web_resources/unknown/path/to/file.ext")
        parser = HtmlContentParser(Mock(build_resource_file_path=Mock(return_value=resource_file_path)), Mock())

        parser._parse_webcontent(Mock(), MagicMock())

        logger_mock.info.assert_called_once_with("Skipping webcontent: %s", resource_file_path)

    @patch("cc2olx.content_parsers.html.logger")
    @patch("cc2olx.content_parsers.html.open", Mock(side_effect=FileNotFoundError))
    def test_webcontent_html_file_reading_failure_is_logged(self, logger_mock):
        parser = HtmlContentParser(Mock(), Mock())
        idref_mock = Mock()
        resource_file_path_mock = Mock()

        with pytest.raises(FileNotFoundError):
            parser._parse_webcontent_html_file(idref_mock, resource_file_path_mock)

        logger_mock.error.assert_called_once_with("Failure reading %s from id %s", resource_file_path_mock, idref_mock)

    @pytest.mark.parametrize(
        "resource,message",
        [
            (
                {"type": "some_type_mock", "href": "https://example.com/some/type/link/"},
                "Not imported content: type = 'some_type_mock', href = 'https://example.com/some/type/link/'",
            ),
            ({"type": "some_type_mock"}, "Not imported content: type = 'some_type_mock'"),
        ],
    )
    @patch("cc2olx.content_parsers.html.logger")
    def test_not_imported_content_parsing_with_href_in_resource(self, logger_mock, resource, message):
        parser = HtmlContentParser(Mock(), Mock())
        expected_content = {"html": message}

        actual_content = parser._parse_not_imported_content(resource)

        logger_mock.info.assert_called_once_with("%s", message)
        assert actual_content == expected_content

    def test_parsing_results(self, cartridge):
        parser = HtmlContentParser(cartridge, Mock())

        assert parser.parse("resource_1_course") == {
            "html": "Not imported content: type = 'associatedcontent/imscc_xmlv1p1/learning-application-resource', "
            "href = 'course_settings/canvas_export.txt'"
        }

        assert parser.parse("resource_3_vertical") == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_3_vertical"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<img src="/static/QuizImages/fractal.jpg" alt="fractal.jpg"'
            ' width="500" height="375" />\n'
            "<p>Fractal Image <a "
            'href="/static/QuizImages/fractal.jpg?canvas_download=1" '
            'target="_blank">Fractal Image</a></p>\n'
            "</body>\n</html>\n"
        }

        assert parser.parse("resource_6_wiki_content") == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_6_wiki_content"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="/jump_to_id/resource_6_wiki_content">Wiki Content</a>'
            "\n</body>\n</html>\n"
        }

        assert parser.parse("resource_7_canvas_content") == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_7_canvas_content"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="/jump_to_id/abc">Canvas Content</a>'
            "\n</body>\n</html>\n"
        }

        assert parser.parse("resource_module-|-introduction") == {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_module-|-introduction"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="/jump_to_id/resource_6_wiki_content">Wiki Content</a>'
            "\n</body>\n</html>\n"
        }
