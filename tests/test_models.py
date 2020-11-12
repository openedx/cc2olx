import zipfile

from pathlib import Path

from cc2olx.models import Cartridge, ResourceFile


def test_cartridge_initialize(imscc_file, settings):
    """
    Tests, that ``Cartridge`` initializes without errors.
    """

    cartridge = Cartridge(imscc_file, settings["workspace"])

    assert cartridge.normalized is None
    assert cartridge.resources is None

    assert isinstance(cartridge.cartridge, zipfile.ZipFile)
    assert cartridge.file_path == imscc_file


def test_load_manifest_extracted(imscc_file, settings, temp_workspace_dir):
    """
    Tests, that all resources and metadata are loaded fine.
    """

    cartridge = Cartridge(imscc_file, settings["workspace"])
    cartridge.load_manifest_extracted()

    cartridge_version = "1.3.0"

    assert cartridge.version == cartridge_version
    assert cartridge.directory == Path(temp_workspace_dir.strpath) / "output" / imscc_file.stem

    assert cartridge.metadata["schema"] == {
        "name": "IMS Common Cartridge", "version": cartridge_version
    }

    assert len(cartridge.resources) == 8
    assert len(cartridge.resources[0]["children"]) == 6
    assert isinstance(cartridge.resources[0]["children"][0], ResourceFile)


def test_cartridge_normalize(imscc_file, settings):
    cartridge = Cartridge(imscc_file, settings["workspace"])
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    assert cartridge.normalized == {
        "children": [
            {
                "children": [
                    {
                        "children": [
                            {
                                "children": [
                                    {
                                        "identifier": "vertical",
                                        "identifierref": "resource_3_vertical",
                                        "title": "Vertical",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Vertical",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "lti",
                                        "identifierref": "resource_2_lti",
                                        "title": "LTI",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "LTI",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "qti",
                                        "identifierref": "resource_4_qti",
                                        "title": "QTI"
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "QTI"
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "discussion_topic_item",
                                        "identifierref": "discussion_topic",
                                        "title": "Discussion",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Discussion",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "image_file",
                                        "title": "Image File Webcontent",
                                        "identifierref": "resource_5_image_file"
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Image File Webcontent",
                            },
                        ],
                        "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                        "identifierref": None,
                        "title": "Sequence",
                    }
                ],
                "identifier": "sequence",
                "identifierref": None,
                "title": "Sequence",
            }
        ],
        "identifier": "org_1",
        "structure": "rooted-hierarchy",
    }


def test_cartridge_get_resource_content(cartridge):
    assert cartridge.get_resource_content("resource_1_course") == (
        "html",
        {
            "html": "Unimported content: type = 'associatedcontent/imscc_xmlv1p1/learning-application-resource', "
                    "href = 'course_settings/canvas_export.txt'"
        }
    )

    assert cartridge.get_resource_content("resource_2_lti") == (
        "lti",
        {
            "title": "Learning Tools Interoperability",
            "description": "https://www.imsglobal.org/activity/learning-tools-interoperability",
            "launch_url": "https://lti.local/launch",
            "height": "500",
            "width": "500",
            "custom_parameters": {}
         }
    )

    assert cartridge.get_resource_content("resource_3_vertical") == (
        'html',
        {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
                    '<title>Vertical</title>\n'
                    '<meta name="identifier" content="resource_3_vertical"/>\n'
                    '<meta name="editing_roles" content="teachers"/>\n'
                    '<meta name="workflow_state" content="active"/>\n'
                    '</head>\n<body>\n'
                    '<img src="%24IMS-CC-FILEBASE%24/QuizImages/fractal.jpg" alt="fractal.jpg"'
                    ' width="500" height="375" />'
                    '\n</body>\n</html>\n'
        }
    )
