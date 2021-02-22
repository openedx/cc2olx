from urllib.parse import parse_qs, urlparse

from cc2olx.link_file_reader import LinkFileReader
from cc2olx.utils import element_builder


class IframeLinkParserError(Exception):
    """
    Exception type for Iframe link parsing errors.
    """


class IframeLinkParser:
    """
    This class forms the base class for all type of link extractor that are being
    written.
    """

    def __init__(self, link_file):
        self.link_map = LinkFileReader(link_file).get_link_map()

    def _extract_src(self, iframe_element):
        """
        Extract the link that iframe is embedding inside it.

        Args:
            iframe_element ([Xml Element]): The iframe tag that is found.

        Returns:
            [str]: The whole URL string which was embedded inside iframe.
        """
        return iframe_element.attrib["src"]

    def _get_video_url(self, iframes):
        """
        This function is responsible to form a proper video URL from the
        polluted URL embeded inside the iframe.

        Args:
            iframes ([Xml Element]): Single iframe tag that is extracted.

        Returns:
            List[str]: List of urls for the iframes.
        """
        urls = []
        for iframe in iframes:
            src = self._extract_src(iframe)
            url = self._extract_url(src)
            urls.append(url)
        return urls

    def _extract_url(self, url):
        """
        This function helps to extract the URL, this URL is the one formed to extract
        the URL that is present in the CSV file. Since the URL has to be formed because
        of the distortion in the iframe embedded.

        Args:
            url ([str]): The iframe embedded URL
        """
        raise NotImplementedError

    def get_video_olx(self, doc, iframes):
        """
        The public function that helps to generate and collect all the
        video OLX and sends it to get written.

        Args:
            doc (XML Document): The document on which the child is formed
            iframes (List[XMl iframe]): List of all the iframes found on the page

        Returns:
            List[Video OLX]: List of video OLX children that is being formed.
            List[iframe]: List of iframes which have been converted to video xblock.
        """
        video_olx_list = []
        converted_iframes = []
        video_urls = self._get_video_url(iframes)
        for url, iframe in zip(video_urls, iframes):
            url_row = self.link_map.get(url)
            if url_row:
                video_olx = self._create_video_olx(doc, url_row)
                video_olx_list.append(video_olx)
                converted_iframes.append(iframe)
        return video_olx_list, converted_iframes

    def _create_video_olx(self, doc, url_row):
        """
        Video OLX generation happens here where each element is generated and a list is prepared.

        Args:
            doc (XML Document): The document on which the child is formed.
            url_row (List[Dict]): The row for that particular URL.

        Returns:
            [Xml child element]: Video OLX element
        """
        xml_element = element_builder(doc)
        attributes = {}
        edx_id = url_row.get("Edx Id", "")
        youtube_id = url_row.get("Youtube Id", "")
        if edx_id.strip() != "":
            attributes["edx_video_id"] = edx_id
        elif youtube_id.strip() != "":
            attributes["youtube"] = "1.00:" + youtube_id
            attributes["youtube_id_1_0"] = youtube_id
        else:
            raise IframeLinkParserError("Missing Edx Id or Youtube Id for video conversion.")
        child = xml_element("video", children=None, attributes=attributes)
        return child


class KalturaIframeLinkParser(IframeLinkParser):
    """
    Link parser for Kaltura videos.
    """

    def __init__(self, link_file):
        super().__init__(link_file)
        self.kalutra_url_format = "{}playManifest/entryId/{}/format/url/protocol/https"

    def _extract_url(self, url):
        """
        This function helps to extract the URL, this URL is the one formed to extract
        the URL that is present in the CSV file. Since the URL has to be formed because
        of the distortion in the iframe embedded.

        Args:
            url ([str]): The iframe embedded URL

        Returns:
            [str]: The csv kaltura URL
        """
        netloc = self._get_netlocation(url)
        entry_id = self._get_entry_id(url)
        if entry_id:
            url = self.kalutra_url_format.format(netloc, entry_id)
        return url

    def _get_netlocation(self, src):
        """
        This helps to get the main URL for Kaltura eg.

        https://cdnapisec.kaltura.com/p/2019031/sp/201903100/
        embedIframeJs/uiconf_id/43123921/partner_id/2019031?
        iframeembed=true&playerId=kaltura_player&entry_id=1_mdkfwzpg

        Args:
            src ([str]): The URL extracted from the iframe.

        Returns:
            [str]: The base URL for kaltura. eg.
            https://cdnapisec.kaltura.com/p/2019031/sp/201903100/
        """
        url = src.split("embedIframeJs")
        net_location = url[0].strip()
        return net_location

    def _get_entry_id(self, src):
        """
        This extracts the entry id from the src URL of iframe.

        Args:
            src ([str]): The URL extracted form the iframe.

        Returns:
            [str]: The entry id for the video.
        """
        entry_id = None
        parsed_url = urlparse(src)
        query = parsed_url.query
        query_dict = parse_qs(query)
        entry_id_query = query_dict.get("entry_id")
        if entry_id_query:
            entry_id = entry_id_query[0]
        return entry_id
