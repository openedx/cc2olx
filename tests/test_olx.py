import tarfile

from cc2olx import olx


def test_olx_export(cartridge, studio_course_xml):
    xml = olx.OlxExport(cartridge).xml()

    assert xml == studio_course_xml


def test_onefile_tar_gz():
    tgz_filename = "test.tar.gz"
    file_content = "content"
    file_name = "test.txt"

    olx.onefile_tar_gz(tgz_filename, file_content.encode("utf8"), file_name)

    with tarfile.open(tgz_filename, "r:gz") as tgz:
        for member in tgz.getmembers():
            assert tgz.extractfile(member).read().decode("utf8") == file_content


def test_convert_link_to_video():
    details = {
        "href": "https://example.com/path"
    }
    details_with_youtube_link = {
        "href": "https://www.youtube.com/watch?v=gQ-cZRmHfs4&amp;amp;list=PL5B350D511278A56B"
    }

    assert olx.convert_link_to_video(details) == ("link", details)
    assert olx.convert_link_to_video(details_with_youtube_link) == (
        "video", {"youtube": "gQ-cZRmHfs4"}
    )
