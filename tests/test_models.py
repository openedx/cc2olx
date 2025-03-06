import zipfile

from cc2olx.models import Cartridge, ResourceFile


def test_cartridge_initialize(imscc_file, options):
    """
    Tests, that ``Cartridge`` initializes without errors.
    """

    cartridge = Cartridge(imscc_file, options["workspace"])

    assert cartridge.normalized is None
    assert cartridge.resources is None

    assert isinstance(cartridge.cartridge, zipfile.ZipFile)
    assert cartridge.file_path == imscc_file


def test_load_manifest_extracted(imscc_file, options, temp_workspace_path):
    """
    Tests, that all resources and metadata are loaded fine.
    """

    cartridge = Cartridge(imscc_file, options["workspace"])
    cartridge.load_manifest_extracted()

    cartridge_version = "1.3.0"

    assert cartridge.version == cartridge_version
    assert cartridge.directory == temp_workspace_path / "output" / imscc_file.stem

    assert cartridge.metadata["schema"] == {
        "name": "IMS Common Cartridge",
        "version": cartridge_version,
    }

    assert len(cartridge.resources) == 24
    assert len(cartridge.resources[0]["children"]) == 6
    assert isinstance(cartridge.resources[0]["children"][0], ResourceFile)


def test_cartridge_normalize(imscc_file, options):
    cartridge = Cartridge(imscc_file, options["workspace"])
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
                                        "identifier": "lti_no_secure_launch_url",
                                        "identifierref": "resource_2_lti_no_secure_launch_url",
                                        "title": "LTI no secure launch URL",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "LTI no secure launch URL",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "qti",
                                        "identifierref": "resource_4_qti",
                                        "title": "QTI",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "QTI",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "qti_no_items",
                                        "identifierref": "resource_4_qti_no_items",
                                        "title": "QTI No Items",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "QTI No Items",
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
                                        "identifierref": "resource_5_image_file",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Image File Webcontent",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "wiki_content",
                                        "identifierref": "resource_6_wiki_content",
                                        "title": "Wiki Content",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Wiki Content",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "canvas_content",
                                        "identifierref": "resource_7_canvas_content",
                                        "title": "Canvas Content",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Canvas Content",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "video",
                                        "identifierref": "resource_5_video",
                                        "title": "Video",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Video",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "video",
                                        "identifierref": "resource_9_video",
                                        "title": "Video With Other Content",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Video With Other Content",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "pdf_web_resource",
                                        "identifierref": "resource_pdf_1",
                                        "title": "PDF from Web Resources",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "PDF from Web Resources",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "pdf_outside_resource",
                                        "identifierref": "resource_pdf_2",
                                        "title": "PDF Outside of Web Resources",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "PDF Outside of Web Resources",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "web_link_content",
                                        "identifierref": "resource_8_web_link_content",
                                        "title": "Web Link Content",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Web Link Content",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "youtube_web_link",
                                        "identifierref": "resource_9_youtube_web_link",
                                        "title": "Django for beginners",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Django for beginners",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "web_link_to_pdf",
                                        "identifierref": "resource_web_link_to_pdf",
                                        "title": "Web Link to PDF file",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Web Link to PDF file",
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
            },
            {
                "children": [
                    {
                        "children": [
                            {
                                "children": [
                                    {
                                        "identifier": "vertical1",
                                        "identifierref": "resource_3_vertical",
                                        "title": "Vertical",
                                    }
                                ],
                                "identifier": "vertical1",
                                "identifierref": "resource_3_vertical",
                                "title": "Vertical",
                            }
                        ],
                        "identifier": "vertical1",
                        "identifierref": "resource_3_vertical",
                        "title": "Vertical",
                    },
                    {
                        "children": [
                            {
                                "children": [
                                    {
                                        "identifier": "subheader1_vertical",
                                        "identifierref": "resource_3_vertical",
                                        "title": "Vertical",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Vertical",
                            }
                        ],
                        "identifier": "subheader1",
                        "identifierref": None,
                        "title": "Sub Header 1",
                    },
                    {
                        "children": [
                            {
                                "children": [
                                    {
                                        "identifier": "subheader2_vertical",
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
                                        "identifier": "external_tool",
                                        "identifierref": "external_tool",
                                        "title": "External Tool",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "External Tool",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "external_tool_retrieve",
                                        "identifierref": "resource_external_tool_retrieve",
                                        "title": "External Tool Retrieve Iframe",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "External Tool Retrieve Iframe",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "assignment_1",
                                        "identifierref": "resource_assignment_1",
                                        "title": "Assignment 1. University education scope essay",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Assignment 1. University education scope essay",
                            },
                            {
                                "children": [
                                    {
                                        "identifier": "assignment_2",
                                        "identifierref": "resource_assignment_2",
                                        "title": "Assignment 2. Television role in education composition",
                                    }
                                ],
                                "identifier": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                "identifierref": None,
                                "title": "Assignment 2. Television role in education composition",
                            },
                        ],
                        "identifier": "subheader2",
                        "identifierref": None,
                        "title": "Sub Header 2",
                    },
                ],
                "identifier": "sequence2",
                "identifierref": None,
                "title": "Sequence2",
            },
        ],
        "identifier": "org_1",
        "structure": "rooted-hierarchy",
    }
