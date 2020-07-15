import tarfile

from unittest.mock import call

from cc2olx.main import convert_one_file, main


def test_convert_one_file(settings, imscc_file, studio_course_xml):
    """
    Tests, that ``convert_one_file`` call for ``imscc`` file results in
    tar.gz archive with olx course.
    """

    convert_one_file(settings, imscc_file)

    tgz_path = imscc_file.parent / "output" / (imscc_file.stem + ".tar.gz")

    with tarfile.open(tgz_path, "r:gz") as tgz:
        for member in tgz.getmembers():
            assert tgz.extractfile(member).read().decode("utf8") == studio_course_xml


def test_main(mocker):
    """
    Tests, that main function tries to invoke convert function for every input file.
    """

    input_files = [
        "file1", "file2", "file3"
    ]

    mocker.patch("cc2olx.main.parse_args")
    settings_mock = mocker.patch("cc2olx.main.collect_settings", return_value={
        "input_files": input_files
    })

    convert_mock = mocker.patch("cc2olx.main.convert_one_file")

    main()

    calls = [call(settings_mock(), input_file) for input_file in input_files]
    convert_mock.assert_has_calls(calls)
