import tarfile

from cc2olx.cli import RESULT_TYPE_ZIP
from cc2olx.main import convert_one_file, main
from .utils import format_xml


def test_convert_one_file(options, imscc_file, studio_course_xml):
    """
    Tests, that ``convert_one_file`` call for ``imscc`` file results in
    tar.gz archive with olx course.
    """
    expected_tgz_members_num = 7

    convert_one_file(
        imscc_file,
        options["workspace"],
        options["link_file"],
        relative_links_source=options["relative_links_source"],
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
