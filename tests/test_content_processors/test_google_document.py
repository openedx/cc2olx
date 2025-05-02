import pytest

from cc2olx.content_processors.dataclasses import ContentProcessorContext
from cc2olx.content_processors.google_document import GoogleDocumentContentProcessor


class TestGoogleDocumentContentProcessor:
    def test_resource_is_not_processed_if_google_document_block_is_not_used(
        self,
        cartridge,
        empty_content_processor_context,
    ):
        processor = GoogleDocumentContentProcessor(cartridge, empty_content_processor_context)
        idref = "resource_google_doc_1"
        resource = cartridge.define_resource(idref)

        assert processor.process(resource, idref) is None

    @pytest.mark.parametrize(
        "not_weblink_webcontent_idref",
        ["resource_6_wiki_content", "resource_5_image_file", "resource_pdf_1", "resource_3_vertical"],
    )
    def test_parse_returns_none_if_resource_is_not_weblink(
        self,
        cartridge,
        not_weblink_webcontent_idref,
    ):
        context = ContentProcessorContext(
            iframe_link_parser=None,
            lti_consumer_ids=set(),
            content_types_with_custom_blocks=["google-document"],
            logs_dir_path=None,
        )
        processor = GoogleDocumentContentProcessor(cartridge, context)
        resource = cartridge.define_resource(not_weblink_webcontent_idref)

        assert processor._parse(resource) is None

    @pytest.mark.parametrize(
        "web_link_url",
        [
            "https://docs.google.com/drawings/d/e/2PACX-1vTDskPsAcSoDz6D0swCEuf9n7R67X0zuaDLIrDorbon9/pub?w=960&h=720",
            "https://docs.google.com/document/u/0/?tgif=d",
            "https://docs.google.com/spreadsheets/u/1/",
            "/2PACX-1vTDskPsAcSoDz6D0swCEuf9n7R67X0zuaDLIrDorbon9/pub?w=960&h=720",
            "https://example.com",
            "http://example.com",
        ],
    )
    def test_transform_web_link_content_to_google_document_when_web_link_points_to_unsupported_url(
        self,
        cartridge,
        web_link_url,
    ):
        context = ContentProcessorContext(
            iframe_link_parser=None,
            lti_consumer_ids=set(),
            content_types_with_custom_blocks=["google-document"],
            logs_dir_path=None,
        )
        processor = GoogleDocumentContentProcessor(cartridge, context)
        web_link_content = {"href": web_link_url}

        assert processor._transform_web_link_content_to_google_document(web_link_content) is None

    @pytest.mark.parametrize(
        "web_link_url",
        [
            "https://docs.google.com/document/d/e/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/edit",
            "https://docs.google.com/document/d/e/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/pub",
            "https://docs.google.com/document/d/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/pub",
            "http://docs.google.com/document/d/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/pub",
            "https://docs.google.com/spreadsheets/d/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/pub",
            "https://docs.google.com/spreadsheets/d/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM",
            "http://docs.google.com/presentation/d/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDM/embed?start=true&loop=true",
            "https://docs.google.com/forms/d/e/2pBGYHuDWfc8lEcAvwZ1ZdCGER59pH7CvyM1WDMWXFZM/alreadyresponded",
        ],
    )
    def test_transform_web_link_content_to_google_document_when_web_link_points_to_supported_url(
        self,
        cartridge,
        web_link_url,
    ):
        context = ContentProcessorContext(
            iframe_link_parser=None,
            lti_consumer_ids=set(),
            content_types_with_custom_blocks=["google-document"],
            logs_dir_path=None,
        )
        processor = GoogleDocumentContentProcessor(cartridge, context)
        web_link_content = {"href": web_link_url}
        expected_content = {"url": web_link_url}

        actual_content = processor._transform_web_link_content_to_google_document(web_link_content)

        assert actual_content == expected_content
