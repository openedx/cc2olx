from urllib.parse import parse_qs, urlparse


class IframeLinkParser:
    def __init__(self, link_map):
        self.link_map = link_map

    def _extract_src(self, iframe_element):
        return iframe_element.attrib['src']

    def _get_video_url(self, iframes):
        urls = []
        for iframe in iframes:
            src = self._extract_src(iframe)
            url = self._extract_url(src)
            urls.append(url)
        return urls

    def get_video_olx(self, doc, iframes):
        video_olx_list = []
        video_urls = self._get_video_url(iframes)
        for url in video_urls:
            url_row = self.link_map[url]
            video_olx = self._create_video_olx(doc, url_row)
            video_olx_list.append(video_olx)
        return video_olx_list

    def _create_video_olx(self, doc, url_row):
        child = doc.createElement("video")
        edx_id = url_row['Edx Id']
        youtube_id = url_row['Youtube Id']
        if youtube_id != '':
            child.setAttribute("youtube", "1.00:" + youtube_id)
            child.setAttribute("youtube_id_1_0", youtube_id)
        if edx_id != '':
            child.setAttribute("edx_video_id", edx_id)
        return child


class KalturaIframeLinkParser(IframeLinkParser):

    def __init__(self, link_map):
        super().__init__(link_map)
        self.kalutra_url_format = "{}playManifest/entryId/{}/format/url/protocol/https"

    def _extract_url(self, url):
        netloc = self._get_netlocation(url)
        entry_id = self._get_entry_id(url)
        url = self.kalutra_url_format.format(netloc, entry_id)
        return url

    def _get_netlocation(self, src):
        url = src.split('embedIframeJs')
        net_location = url[0]
        return net_location

    def _get_entry_id(self, src):
        parsed_url = urlparse(src)
        query = parsed_url.query
        query_dict = parse_qs(query)
        entry_id = query_dict['entry_id'][0]
        return entry_id
