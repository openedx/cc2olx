import tarfile

from cc2olx.main import convert_one_file


def test_convert_one_file(settings, imscc_file):
    """
    Tests, that ``convert_one_file`` call over ``imscc`` file results in
    tar.gz archive with olx course.
    """

    convert_one_file(settings, imscc_file)

    tgz_path = imscc_file.parent / "tmp" / (imscc_file.stem + ".tar.gz")

    course_xml_content = "<?xml version=\"1.0\" ?>\n"\
                         "<!-- Generated by cc2olx -->\n" \
                         "<course course=\"Some_cc_Course\" name=\"The Life of Paul\" org=\"org\"/>\n"

    with tarfile.open(tgz_path, "r:gz") as tgz:
        for member in tgz.getmembers():
            assert tgz.extractfile(member).read().decode("utf8") == course_xml_content
