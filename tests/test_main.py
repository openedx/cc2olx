import tarfile

from cc2olx.cli import RESULT_TYPE_ZIP
from cc2olx.main import convert_one_file, main


def test_convert_one_file(settings, imscc_file, studio_course_xml):
    """
    Tests, that ``convert_one_file`` call for ``imscc`` file results in
    tar.gz archive with olx course.
    """

    convert_one_file(imscc_file, settings["workspace"])

    tgz_path = str((imscc_file.parent / "output" / imscc_file.stem).with_suffix(".tar.gz"))

    with tarfile.open(tgz_path, "r:gz") as tgz:
        for member in tgz.getmembers():
            assert tgz.extractfile(member).read().decode("utf8") == studio_course_xml


def test_main(mocker, imscc_file, settings):
    """
    Tests, that invocation of main function results in converted ``.imscc`` file.
    """

    mocker.patch("cc2olx.main.parse_args")
    mocker.patch("cc2olx.main.collect_settings", return_value=settings)

    main()

    # workspace has been created
    assert settings["workspace"].exists()

    # content of imscc has been extracted
    assert (settings["workspace"] / imscc_file.stem).exists()

    # archived olx course has been generated
    assert (settings["workspace"] / imscc_file.stem).with_suffix(".tar.gz").exists()


def test_main_zip_output(mocker, settings):
    """
    Tests, that ``--result zip`` cli option works fine.
    """

    settings["output_format"] = RESULT_TYPE_ZIP

    mocker.patch("cc2olx.main.parse_args")
    mocker.patch("cc2olx.main.collect_settings", return_value=settings)

    main()

    assert settings["workspace"].with_suffix(".zip").exists()
