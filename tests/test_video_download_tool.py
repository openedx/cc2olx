from argparse import Namespace
from unittest.mock import call, Mock

from cc2olx.tools.video_download import (
    parse_args,
    find_all_video_urls,
    reformat,
    get_ydl_opts,
    write_csv,
    main,
    download_videos,
)


def test_find_video_urls_in_html(fixtures_data_dir):
    """
    Basic test for extracting Kaltura URLs.
    """

    html_file_path = str(fixtures_data_dir / "imscc_file" / "iframe.html")
    urls = find_all_video_urls(html_file_path)
    urls = [reformat(u) for u in urls]
    expected = [
        "https://cdnapisec.kaltura.com/p/2019031/sp/201903100/playManifest/entryId/1_zeqnrfgw/format/url/protocol/https"
    ]
    assert urls == expected


def test_find_all_video_urls_in_cc(imscc_file):
    """
    Basic test for extracting Kaltura URLs.
    """

    urls = find_all_video_urls(imscc_file)
    urls = [reformat(u) for u in urls]
    expected = [
        "https://cdnapisec.kaltura.com/p/2019031/sp/201903100/playManifest/entryId/1_zeqnrfgw/format/url/protocol/https",  # noqa: E501
        "https://cdnapisec.kaltura.com/p/2019031/sp/201903100/playManifest/entryId/1_zeqnrfgw/format/url/protocol/https",  # noqa: E501
        "https://www.youtube.com/watch?v=zE-a5eqvlv8",
    ]
    assert urls == expected


def test_parse_args(imscc_file):
    """
    Basic cli test.
    """

    parsed_args = parse_args(["-i", str(imscc_file), "-o", "outfile.csv", "-d", "download_dir", "-v"])

    assert parsed_args == Namespace(
        input=str(imscc_file), config=None, output="outfile.csv", downloads="download_dir", simulate=False, verbose=True
    )


def test_ydl_opts():
    """
    Basic test of youtube-dl options.
    """

    parsed_args = parse_args(["-i", "file.html", "-d", "download_dir", "-v", "-s"])
    opts = get_ydl_opts(parsed_args)

    assert opts["verbose"]
    assert opts["simulate"]
    assert opts["outtmpl"] == "download_dir/%(title)s.%(ext)s"


def test_write_csv(mocker):
    csv_writerow_mock = mocker.patch("csv.DictWriter.writerow")

    urls = ["url1", "url2", "youtube.com/watch?v=1234"]
    relpaths = ["rel1", "rel2", "rel3"]

    write_csv("outfile", urls, relpaths)

    expected_csv_writerow_call_args = [
        call(
            {
                "Relative File Path": "Relative File Path",
                "External Video Link": "External Video Link",
                "Youtube Id": "Youtube Id",
            }
        ),
        call(
            {
                "Relative File Path": "rel1",
                "External Video Link": "url1",
                "Youtube Id": "",
            }
        ),
        call(
            {
                "Relative File Path": "rel2",
                "External Video Link": "url2",
                "Youtube Id": "",
            }
        ),
        call(
            {
                "Relative File Path": "rel3",
                "External Video Link": "youtube.com/watch?v=1234",
                "Youtube Id": "1234",
            }
        ),
    ]

    csv_writerow_mock.assert_has_calls(expected_csv_writerow_call_args, any_order=True)


class FakeYDL:
    def __init__(self, opts):
        self.opts = opts

    def download(self, urls):
        for url in urls:
            for hook in self.opts["progress_hooks"]:
                hook({"status": "finished", "filename": "filename.mp4"})


def test_main(mocker, imscc_file):
    args_mock = Mock()
    args_mock.configure_mock(config=None, input=imscc_file, output="outfileXXX", simulate=True)
    mocker.patch("cc2olx.tools.video_download.parse_args", return_value=args_mock)
    mocker.patch("cc2olx.tools.video_download.youtube_dl.YoutubeDL", new=FakeYDL)

    csv_writerow_mock = mocker.patch("csv.DictWriter.writerow")

    main()

    expected_csv_writerow_call_args = [
        call(
            {
                "Relative File Path": "Relative File Path",
                "External Video Link": "External Video Link",
                "Youtube Id": "Youtube Id",
            }
        ),
        call(
            {
                "Relative File Path": "filename.mp4",
                "External Video Link": "https://cdnapisec.kaltura.com/p/2019031/sp/201903100/playManifest/entryId/1_zeqnrfgw/format/url/protocol/https",  # noqa: E501
                "Youtube Id": "",
            }
        ),
        call(
            {
                "Relative File Path": "filename.mp4",
                "External Video Link": "https://cdnapisec.kaltura.com/p/2019031/sp/201903100/playManifest/entryId/1_zeqnrfgw/format/url/protocol/https",  # noqa: E501
                "Youtube Id": "",
            }
        ),
    ]

    csv_writerow_mock.assert_has_calls(expected_csv_writerow_call_args, any_order=True)


def test_download_videos(mocker):
    parsed_args = parse_args(["-i", "file.html", "-d", "download_dir", "-v", "-s"])
    opts = get_ydl_opts(parsed_args)
    mocker.patch("cc2olx.tools.video_download.youtube_dl.YoutubeDL", return_value=FakeYDL(opts))
    ret = download_videos(["url1", "url2", "url3"], opts)
    assert ret == ["filename.mp4", "filename.mp4", "filename.mp4"]
