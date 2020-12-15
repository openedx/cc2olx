from lxml import html
import pytest
import xml.dom.minidom

from cc2olx.iframe_link_parser import KalturaIframeLinkParser


@pytest.fixture(scope="session")
def iframe_link_parser(link_map_csv):
    """
        This fixture provides us with the Kaltura parser.
    Args:
        link_map_csv ([str]): Link file path.

    Returns:
        [Iframe Link Parse]: Instance of link parser class.
    """
    iframe_link_parser = KalturaIframeLinkParser(link_map_csv)
    return iframe_link_parser


@pytest.fixture(scope="session")
def iframes(iframe_content):
    """
        The fixture to extract iframe from html string.
    Args:
        iframe_content ([str]): The content of the HTML file.

    Returns:
        List[iframe]: List of iframe DOM elements.
    """
    parsed_html = html.fromstring(iframe_content)
    iframes = parsed_html.xpath("//iframe")
    return iframes


@pytest.fixture(scope="session")
def video_olx_list(iframe_link_parser, iframes):
    """
        Fixture to provide list of video OLX elements.
    Args:
        iframe_link_parser (Iframe Link Parse): Link Parser.
        iframes ([Xml DOM Element]): XML DOM Element.

    Returns:
        List[Video OLX Element]: List of video OLX element.
    """
    doc = xml.dom.minidom.Document()
    video_olx, _ = iframe_link_parser.get_video_olx(doc, iframes)
    return video_olx


class TestKalturaIframeLinkParse:
    """
    The class responsible to test kaltura iframe link parser.
    """

    def test_video_olx_generation(self, video_olx_list):
        """
        Test if video olx is generated.

        Args:
            iframe_link_parser ([Iframe Link Parse]): Parser class.
            iframes ([type]): iframe DOM element.
        """
        assert len(video_olx_list) == 1

    def test_video_olx_produced(self, video_olx_list):
        """
        Test the structure of the video xblock formed is right.

        Args:
            video_olx_list (List[Xml element]): List of video xblocks.
        """
        # Example of video element
        # '<video edx_video_id="42d2a5e2-bced-45d6-b8dc-2f5901c9fdd0"/>\n'  # noqa: E501
        actual_video_olx = video_olx_list[0]
        assert actual_video_olx.hasAttribute('edx_video_id')

    def test_get_netlocation(self, iframe_link_parser):
        """
        Test the extraction of base URL.

        Args:
            iframe_link_parser ([Kaltura Link Parser]): Kaltura Link Parser.
        """
        url = "https://cdnapisec.kaltura.com/p/2019031/sp/201903100/ \
        embedIframeJs/uiconf_id/43123921/partner_id/2019031 \
        ?iframeembed=true&playerId=kaltura_player&entry_id=1_mdkfwzpg"
        base_url = iframe_link_parser._get_netlocation(url)
        assert base_url == "https://cdnapisec.kaltura.com/p/2019031/sp/201903100/"

    def test_get_entry_id(self, iframe_link_parser):
        """
        Test entry id extraction.

        Args:
            iframe_link_parser ([Kaltura Link Parser]): Kaltura Link Parser.
        """
        url = "https://cdnapisec.kaltura.com/p/2019031/sp/201903100/ \
        embedIframeJs/uiconf_id/43123921/partner_id/2019031 \
        ?iframeembed=true&playerId=kaltura_player&entry_id=1_mdkfwzpg"
        entry_id = iframe_link_parser._get_entry_id(url)
        assert entry_id == "1_mdkfwzpg"

    def test_extract_url(self, iframe_link_parser):
        """
        Test extracted URL.

        Args:
            iframe_link_parser ([Kaltura Link Parser]): Kaltura Link Parser.
        """
        url = "https://cdnapisec.kaltura.com/p/2019031/sp/201903100/ \
        embedIframeJs/uiconf_id/43123921/partner_id/2019031 \
        ?iframeembed=true&playerId=kaltura_player&entry_id=1_mdkfwzpg"
        extracted_url = iframe_link_parser._extract_url(url)
        expected_url = "https://cdnapisec.kaltura.com/p/2019031/sp/201903100/playManifest/entryId/1_mdkfwzpg/format/url/protocol/https"  # noqa: E501
        assert extracted_url == expected_url
