import pytest

from cc2olx.content_processors.dataclasses import ContentProcessorContext
from cc2olx.content_processors.pdf import PDFContentProcessor


class TestPdfContentProcessor:
    def test_resource_is_not_processed_if_pdf_block_is_not_used(self, cartridge, empty_content_processor_context):
        processor = PDFContentProcessor(cartridge, empty_content_processor_context)
        idref = "resource_pdf_1"
        resource = cartridge.define_resource(idref)

        assert processor.process(resource, idref) is None

    @pytest.mark.parametrize(
        "not_pdf_webcontent_idref",
        ["resource_6_wiki_content", "resource_5_image_file", "resource_7_canvas_content", "resource_3_vertical"],
    )
    def test_parse_webcontent_returns_none_if_resource_file_is_not_pdf(self, cartridge, not_pdf_webcontent_idref):
        context = ContentProcessorContext(
            iframe_link_parser=None,
            lti_consumer_ids=set(),
            content_types_with_custom_blocks=["pdf"],
            logs_dir_path=None,
        )
        processor = PDFContentProcessor(cartridge, context)
        resource = cartridge.define_resource(not_pdf_webcontent_idref)

        assert processor._parse_webcontent(resource) is None

    @pytest.mark.parametrize(
        "web_link_url",
        ["https://example.com/html_content.html", "http://example.com/video.mp4", "/path/to/audio.wav"],
    )
    def test_transform_web_link_content_to_pdf_returns_none_if_web_link_does_not_point_to_pdf_file(
        self,
        cartridge,
        web_link_url,
    ):
        context = ContentProcessorContext(
            iframe_link_parser=None,
            lti_consumer_ids=set(),
            content_types_with_custom_blocks=["pdf"],
            logs_dir_path=None,
        )
        processor = PDFContentProcessor(cartridge, context)
        web_link_content = {"href": web_link_url}

        assert processor._transform_web_link_content_to_pdf(web_link_content) is None

    @pytest.mark.parametrize(
        "web_link_url",
        ["https://example.com/PEP_8.pdf", "http://example.com/imscc_profilev1p2-Overview.pdf", "/static/example.pdf"],
    )
    def test_transform_web_link_content_to_pdf_when_web_link_points_to_pdf_file(self, cartridge, web_link_url):
        context = ContentProcessorContext(
            iframe_link_parser=None,
            lti_consumer_ids=set(),
            content_types_with_custom_blocks=["pdf"],
            logs_dir_path=None,
        )
        processor = PDFContentProcessor(cartridge, context)
        web_link_content = {"href": web_link_url}
        expected_content = {"url": web_link_url}

        actual_content = processor._transform_web_link_content_to_pdf(web_link_content)

        assert actual_content == expected_content
