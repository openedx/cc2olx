import tarfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from cc2olx.cli import RESULT_TYPE_ZIP
from cc2olx.main import _output_converting_logs, convert_one_file, main
from .utils import format_xml


def test_convert_one_file(options, imscc_file, studio_course_xml):
    """
    Tests, that ``convert_one_file`` call for ``imscc`` file results in
    tar.gz archive with olx course.
    """
    expected_tgz_members_num = 8

    convert_one_file(
        imscc_file,
        options["workspace"],
        options["link_file"],
        relative_links_source=options["relative_links_source"],
        content_types_with_custom_blocks=options["content_types_with_custom_blocks"],
    )

    tgz_path = str((imscc_file.parent / "output" / imscc_file.stem).with_suffix(".tar.gz"))

    with tarfile.open(tgz_path, "r:gz") as tgz:
        tgz_members = tgz.getmembers()

        assert len(tgz_members) == expected_tgz_members_num

        for member in tgz_members:
            if member.name == "course.xml":
                expected = tgz.extractfile(member).read().decode("utf8")
                assert format_xml(expected) == format_xml(studio_course_xml)
                break


def test_main(mocker, imscc_file, options):
    """
    Tests, that invocation of main function results in converted ``.imscc`` file.
    """

    mocker.patch("cc2olx.main.parse_args")
    mocker.patch("cc2olx.main.parse_options", return_value=options)

    main()

    # workspace has been created
    assert options["workspace"].exists()

    # content of imscc has been extracted
    assert (options["workspace"] / imscc_file.stem).exists()

    # archived olx course has been generated
    assert (options["workspace"] / imscc_file.stem).with_suffix(".tar.gz").exists()


def test_main_zip_output(mocker, options):
    """
    Tests, that ``--result zip`` cli option works fine.
    """

    options["output_format"] = RESULT_TYPE_ZIP

    mocker.patch("cc2olx.main.parse_args")
    mocker.patch("cc2olx.main.parse_options", return_value=options)

    main()

    assert options["workspace"].with_suffix(".zip").exists()


def test_file_converting_failure_is_logged(mocker, options):
    """
    Test it is logged when the file converting is failed.
    """
    mocker.patch("cc2olx.main.parse_args")
    mocker.patch("cc2olx.main.parse_options", return_value=options)
    mocker.patch("cc2olx.main.convert_one_file", side_effect=Exception("Some error occurred."))
    log_file_converting_failure_mock = mocker.patch("cc2olx.main._log_file_converting_failure")

    main()

    log_file_converting_failure_mock.assert_called_once()


def test_converting_logs_are_outputted(mocker):
    """
    Test the case when converting logs are outputted.
    """
    logs_dir = "/logs/dir/path"
    logs_dir_path = Path(logs_dir)
    temp_logs_dir = "/temp/logs/dir/path"
    temp_logs_dir_path_mock = Mock(exists=Mock(return_value=True), __str__=Mock(return_value=temp_logs_dir))
    shutil_mock = mocker.patch("cc2olx.main.shutil")

    _output_converting_logs(logs_dir_path, temp_logs_dir_path_mock)

    shutil_mock.rmtree.assert_called_once_with(logs_dir, ignore_errors=True)
    shutil_mock.copytree.assert_called_once_with(temp_logs_dir, logs_dir)


@pytest.mark.parametrize("temp_logs_dir_path_mock", (None, Mock(exists=Mock(return_value=False))))
def test_converting_logs_are_not_outputted(mocker, temp_logs_dir_path_mock):
    """
    Test the case when converting logs are not outputted.
    """
    shutil_mock = mocker.patch("cc2olx.main.shutil")

    _output_converting_logs(Mock(), temp_logs_dir_path_mock)

    shutil_mock.rmtree.assert_not_called()
    shutil_mock.copytree.assert_not_called()
