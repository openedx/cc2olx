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
    video_olx = iframe_link_parser.get_video_olx(doc, iframes)
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
            Examples:
        Args:
            video_olx_list (List[Xml element]): List of video xblocks.
        """
        # Example of video element
        # '<video edx_video_id="42d2a5e2-bced-45d6-b8dc-2f5901c9fdd0" youtube="1.00:onRUvL2SBG8" youtube_id_1_0="onRUvL2SBG8"/>\n'  # noqa: E501
        actual_video_olx = video_olx_list[0]
        assert actual_video_olx.hasAttribute('edx_video_id')
        assert actual_video_olx.hasAttribute('youtube')
