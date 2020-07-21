# flake8: noqa: E501

import os
import shutil
import zipfile

from pathlib import Path
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
def settings(imscc_file):
    """
    Basic settings fixture.
    """

    parsed_args = parse_args(["-i", str(imscc_file)])

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
