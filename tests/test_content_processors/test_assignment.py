import pytest

from cc2olx.content_processors.assignment import AssignmentContentProcessor


class TestAssignmentContentProcessor:
    @pytest.mark.parametrize(
        "is_textual_submission_allowed,is_file_submission_allowed,expected_text_response",
        [
            (True, True, "optional"),
            (True, False, "required"),
            (False, True, ""),
            (False, False, "required"),
        ],
    )
    def test_get_text_response_results(
        self,
        is_textual_submission_allowed,
        is_file_submission_allowed,
        expected_text_response,
        cartridge,
        empty_content_processor_context,
    ):
        processor = AssignmentContentProcessor(cartridge, empty_content_processor_context)

        actual_text_response = processor._get_text_response(is_textual_submission_allowed, is_file_submission_allowed)

        assert actual_text_response == expected_text_response

    @pytest.mark.parametrize(
        "is_textual_submission_allowed,is_file_submission_allowed,expected_text_response",
        [
            (True, True, "optional"),
            (True, False, ""),
            (False, True, "required"),
            (False, False, ""),
        ],
    )
    def test_get_file_upload_response_results(
        self,
        is_textual_submission_allowed,
        is_file_submission_allowed,
        expected_text_response,
        cartridge,
        empty_content_processor_context,
    ):
        processor = AssignmentContentProcessor(cartridge, empty_content_processor_context)

        actual_text_response = processor._get_file_upload_response(
            is_textual_submission_allowed,
            is_file_submission_allowed,
        )

        assert actual_text_response == expected_text_response

    @pytest.mark.parametrize(
        "accepted_format_types,expected_editor",
        [
            (set(), "text"),
            ({"html"}, "tinymce"),
            ({"text"}, "text"),
            ({"file"}, "text"),
            ({"file", "url"}, "text"),
            ({"text", "file", "url"}, "text"),
            ({"text", "html"}, "tinymce"),
            ({"html", "url"}, "tinymce"),
            ({"text", "html", "file", "url"}, "tinymce"),
        ],
    )
    def test_get_text_response_editor_results(
        self,
        accepted_format_types,
        expected_editor,
        cartridge,
        empty_content_processor_context,
    ):
        processor = AssignmentContentProcessor(cartridge, empty_content_processor_context)

        actual_editor = processor._get_text_response_editor(accepted_format_types)

        assert actual_editor == expected_editor

    @pytest.mark.parametrize(
        "accepted_format_types,is_file_submission_allowed",
        [
            (set(), False),
            ({"html"}, False),
            ({"text"}, False),
            ({"url"}, False),
            ({"file"}, True),
            ({"html", "text"}, False),
            ({"html", "file"}, True),
            ({"url", "file"}, True),
            ({"html", "text", "url"}, False),
            ({"html", "text", "url", "file"}, True),
        ],
    )
    def test_is_file_submission_allowed_results(
        self,
        accepted_format_types,
        is_file_submission_allowed,
        cartridge,
        empty_content_processor_context,
    ):
        processor = AssignmentContentProcessor(cartridge, empty_content_processor_context)

        assert processor._is_file_submission_allowed(accepted_format_types) is is_file_submission_allowed

    @pytest.mark.parametrize(
        "accepted_format_types,is_textual_submission_allowed",
        [
            (set(), False),
            ({"html"}, True),
            ({"text"}, True),
            ({"url"}, True),
            ({"file"}, False),
            ({"html", "text"}, True),
            ({"text", "url"}, True),
            ({"html", "file"}, True),
            ({"html", "text", "url"}, True),
            ({"html", "text", "url", "file"}, True),
        ],
    )
    def test_is_textual_submission_allowed_results(
        self,
        accepted_format_types,
        is_textual_submission_allowed,
        cartridge,
        empty_content_processor_context,
    ):
        processor = AssignmentContentProcessor(cartridge, empty_content_processor_context)

        assert processor._is_textual_submission_allowed(accepted_format_types) is is_textual_submission_allowed

    @pytest.mark.parametrize("file_upload_response", ("optional", "required"))
    def test_default_file_upload_types_are_used_if_file_submission_allowed(
        self,
        file_upload_response,
        cartridge,
        empty_content_processor_context,
    ):
        processor = AssignmentContentProcessor(cartridge, empty_content_processor_context)

        assert processor._get_file_upload_type(file_upload_response) == "pdf-and-image"

    def test_no_file_upload_types_are_used_if_file_submission_is_not_allowed(
        self,
        cartridge,
        empty_content_processor_context,
    ):
        processor = AssignmentContentProcessor(cartridge, empty_content_processor_context)

        assert processor._get_file_upload_type("") is None

    @pytest.mark.parametrize("file_upload_response", ("optional", "required"))
    def test_default_file_types_are_white_listed_if_file_submission_allowed(
        self,
        file_upload_response,
        cartridge,
        empty_content_processor_context,
    ):
        processor = AssignmentContentProcessor(cartridge, empty_content_processor_context)
        expected_file_types = ["pdf", "gif", "jpg", "jpeg", "jfif", "pjpeg", "pjp", "png"]

        assert processor._get_white_listed_file_types(file_upload_response) == expected_file_types

    def test_no_file_types_are_white_listed_if_file_submission_is_not_allowed(
        self,
        cartridge,
        empty_content_processor_context,
    ):
        processor = AssignmentContentProcessor(cartridge, empty_content_processor_context)

        assert processor._get_white_listed_file_types("") == []
