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
from cc2olx.settings import collect_settings


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


@pytest.fixture
def settings(imscc_file, link_map_csv):
    """
    Basic settings fixture.
    """

    parsed_args = parse_args(["-i", str(imscc_file), "-f", str(link_map_csv)])

    _settings = collect_settings(parsed_args)

    yield _settings

    shutil.rmtree(_settings["workspace"], ignore_errors=True)


@pytest.fixture
def cartridge(imscc_file, settings):
    cartridge = Cartridge(imscc_file, settings["workspace"])
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    yield cartridge

    shutil.rmtree(str(settings["workspace"] / imscc_file.stem))

@pytest.fixture(scope="session")
def video_upload_args(fixtures_data_dir):
    return {
        'course_id': 'course-v1:edX+111222+111222',
        'directory': str(fixtures_data_dir.joinpath('video_files')),
        'input_csv': str(fixtures_data_dir.joinpath('video-data.csv')),
        'output_csv': NamedTemporaryFile().name,
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
def iframe_content(fixtures_data_dir):
    """
        This fixture gives out the html content of the file.
    Args:
        fixtures_data_dir ([str]): Path to the directory where fixture data is present.

    Returns:
        [str]: String content of html file
    """

    html_file_path = str(fixtures_data_dir / "imscc_file" / "iframe.html")
    with open(html_file_path, 'r') as htmlcontent:
        content = htmlcontent.read()
    return content
