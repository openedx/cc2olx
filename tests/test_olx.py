from cc2olx import olx


def test_olx_export(cartridge, studio_course_xml):
    xml = olx.OlxExport(cartridge).xml()

    assert xml == studio_course_xml


def test_process_link():
    details = {
        "href": "https://example.com/path"
    }
    details_with_youtube_link = {
        "href": "https://www.youtube.com/watch?v=gQ-cZRmHfs4&amp;amp;list=PL5B350D511278A56B"
    }

    assert olx.process_link(details) == (
        "html", {"html": "<a href='{}'></a>".format(details["href"])}
    )

    assert olx.process_link(details_with_youtube_link) == (
        "video", {"youtube": "gQ-cZRmHfs4"}
    )
