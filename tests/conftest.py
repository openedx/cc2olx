# flake8: noqa: E501

import os
import shutil
import zipfile

from pathlib import Path
from tempfile import NamedTemporaryFile
from xml.dom.minidom import parse

import pytest

from cc2olx.cli import parse_args
from cc2olx.models import Cartridge
from cc2olx.parser import parse_options


@pytest.fixture(scope="session")
def fixtures_data_dir():
    return Path(__file__).parent / "fixtures_data"


@pytest.fixture(scope="session")
def temp_workspace_dir(tmpdir_factory):
    """
    Temporary workspace directory.
    """

    return tmpdir_factory.mktemp("workspace")


@pytest.fixture(scope="session")
def chdir_to_workspace(temp_workspace_dir):
    """
    Changes current working directory to ``pytest`` temporary directory.
    """

    old_working_dir = Path.cwd()
    os.chdir(temp_workspace_dir.strpath)

    yield

    os.chdir(str(old_working_dir))


@pytest.fixture(scope="session")
def imscc_file(temp_workspace_dir, fixtures_data_dir):
    """
    Creates zip file with ``.imscc`` extension and all files
    from fixture_data/imscc_file directory.
    """

    fixture_data = fixtures_data_dir / "imscc_file"

    result_path = Path(temp_workspace_dir.strpath) / "course.imscc"

    with zipfile.ZipFile(str(result_path), "w") as zf:
        for cc_file in fixture_data.rglob("*"):
            if cc_file.is_file():
                zf.write(str(cc_file), str(cc_file.relative_to(fixture_data)))

    return result_path


@pytest.fixture(scope="session")
def studio_course_xml(fixtures_data_dir):
    """
    xml string of converted Common Cartridge course.

    NOTE: related xml file from fixtures_data directory must be updated when
    ``imscc_file`` fixture's files updated.
    """

    course_xml_filename = str(fixtures_data_dir / "studio_course_xml" / "course.xml")

    return parse(course_xml_filename).toprettyxml()


@pytest.fixture(scope="session")
def relative_links_source() -> str:
    """
    Provide a relative links source.
    """
    return "https://relative.source.domain"


@pytest.fixture
def options(imscc_file, link_map_csv, relative_links_source):
    """
    Basic options fixture.
    """

    args = parse_args(["-i", str(imscc_file), "-f", str(link_map_csv), "-s", relative_links_source])

    options = parse_options(args)

    yield options

    shutil.rmtree(options["workspace"], ignore_errors=True)


@pytest.fixture
def cartridge(imscc_file, options):
    cartridge = Cartridge(imscc_file, options["workspace"])
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    yield cartridge

    shutil.rmtree(str(options["workspace"] / imscc_file.stem))


@pytest.fixture(scope="session")
def video_upload_args(fixtures_data_dir):
    return {
        "course_id": "course-v1:edX+111222+111222",
        "directory": str(fixtures_data_dir.joinpath("video_files")),
        "input_csv": str(fixtures_data_dir.joinpath("video-data.csv")),
        "output_csv": NamedTemporaryFile().name,
    }


@pytest.fixture(scope="session")
def link_map_csv(fixtures_data_dir):
    """
        This fixture helps to provide csv file path
    Args:
        fixtures_data_dir ([str]): Path to the directory where fixture data is present.

    Returns:
        [str]: Path to the csv
    """

    link_map_csv_file_path = str(fixtures_data_dir / "link_map.csv")
    return link_map_csv_file_path


@pytest.fixture(scope="session")
def link_map_languages_csv(fixtures_data_dir):
    """
        This fixture helps to provide csv file path with transcript languages included
    Args:
        fixtures_data_dir ([str]): Path to the directory where fixture data is present.

    Returns:
        [str]: Path to the csv
    """

    link_map_csv_file_path = str(fixtures_data_dir / "link_map_languages.csv")
    return link_map_csv_file_path


@pytest.fixture(scope="session")
def link_map_edx_only_csv(fixtures_data_dir):
    """
        This fixture helps to provide csv file path to a csv containing only the edX Id
    Args:
        fixtures_data_dir ([str]): Path to the directory where fixture data is present.

    Returns:
        [str]: Path to the csv
    """

    link_map_csv_file_path = str(fixtures_data_dir / "link_map_edx_only.csv")
    return link_map_csv_file_path


@pytest.fixture(scope="session")
def link_map_youtube_only_csv(fixtures_data_dir):
    """
        This fixture helps to provide csv file path to a csv containing only the youtube Id
    Args:
        fixtures_data_dir ([str]): Path to the directory where fixture data is present.

    Returns:
        [str]: Path to the csv
    """

    link_map_csv_file_path = str(fixtures_data_dir / "link_map_youtube_only.csv")
    return link_map_csv_file_path


@pytest.fixture(scope="session")
def link_map_bad_csv(fixtures_data_dir):
    """
        This fixture helps to provide csv file path containing neither edX nor youtube Id
    Args:
        fixtures_data_dir ([str]): Path to the directory where fixture data is present.

    Returns:
        [str]: Path to the csv
    """

    link_map_csv_file_path = str(fixtures_data_dir / "link_map_bad.csv")
    return link_map_csv_file_path


@pytest.fixture(scope="session")
def iframe_content(fixtures_data_dir):
    """
        This fixture gives out the html content of the file.
    Args:
        fixtures_data_dir ([str]): Path to the directory where fixture data is present.

    Returns:
        [str]: String content of html file
    """

    html_file_path = str(fixtures_data_dir / "imscc_file" / "iframe.html")
    with open(html_file_path, "r", encoding="utf-8") as htmlcontent:
        content = htmlcontent.read()
    return content


@pytest.fixture(scope="session")
def passports_csv(fixtures_data_dir):
    """
    This fixture helps to provide a valid passports csv file containing all the
    required headers.

    Args:
        fixtures_data_dir ([str]): Path to the directory where fixture data is present.

    Returns:
        [str]: Path to the csv
    """
    passports_file_path = str(fixtures_data_dir / "passports.csv")
    return passports_file_path


@pytest.fixture(scope="session")
def bad_passports_csv(fixtures_data_dir):
    """
    This fixture helps to provide a valid passports csv file which does not contain
    all the required headers.

    Args:
        fixtures_data_dir ([str]): Path to the directory where fixture data is present.

    Returns:
        [str]: Path to the csv
    """
    bad_passports_csv = str(fixtures_data_dir / "bad_passports.csv")
    return bad_passports_csv


@pytest.fixture(scope="session")
def transcript_file(fixtures_data_dir):
    transcript_file_path = str(
        fixtures_data_dir / "video_files/01___Intro_to_Knowledge_Based_AI/0 - Introductions.en.srt"
    )
    return transcript_file_path


@pytest.fixture(scope="session")
def html_without_cdata(fixtures_data_dir: Path) -> str:
    """
    HTML string that doesn't contain CDATA sections.

    Args:
        fixtures_data_dir (str): Path to the directory where fixture data is present.

    Returns:
        str: HTML string.
    """
    html_without_cdata_path = fixtures_data_dir / "html_files/html-without-cdata.html"
    return html_without_cdata_path.read_text()


@pytest.fixture(scope="session")
def cdata_containing_html(fixtures_data_dir: Path) -> str:
    """
    HTML string that contains CDATA sections.

    Args:
        fixtures_data_dir (str): Path to the directory where fixture data is present.

    Returns:
        str: HTML string.
    """
    html_without_cdata_path = fixtures_data_dir / "html_files/cdata-containing-html.html"
    return html_without_cdata_path.read_text()


@pytest.fixture(scope="session")
def expected_cleaned_cdata_containing_html(fixtures_data_dir: Path) -> str:
    """
    The string with expected HTML after cleaning from CDATA sections.

    Args:
        fixtures_data_dir (str): Path to the directory where fixture data is present.

    Returns:
        str: HTML string.
    """
    html_without_cdata_path = fixtures_data_dir / "html_files/cleaned-cdata-containing-html.html"
    return html_without_cdata_path.read_text()
