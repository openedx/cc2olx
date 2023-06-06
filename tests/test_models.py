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
        "name": "IMS Common Cartridge",
        "version": cartridge_version,
    }

    assert len(cartridge.resources) == 20
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
                                        "identifier": "pdf_outside_resource",
                                        "identifierref": "pdf_dependency",
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


def test_cartridge_get_resource_content(cartridge):
    assert cartridge.get_resource_content("resource_1_course") == (
        "html",
        {
            "html": "Unimported content: type = 'associatedcontent/imscc_xmlv1p1/learning-application-resource', "
            "href = 'course_settings/canvas_export.txt'"
        },
    )

    assert cartridge.get_resource_content("resource_2_lti") == (
        "lti",
        {
            "title": "Learning Tools Interoperability",
            "description": "https://www.imsglobal.org/activity/learning-tools-interoperability",
            "launch_url": "https://lti.local/launch",
            "height": "500",
            "width": "500",
            "custom_parameters": {},
            "lti_id": "learning_tools_interoperability",
        },
    )

    assert cartridge.get_resource_content("resource_3_vertical") == (
        "html",
        {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_3_vertical"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<img src="%24IMS-CC-FILEBASE%24/QuizImages/fractal.jpg" alt="fractal.jpg"'
            ' width="500" height="375" />\n'
            "<p>Fractal Image <a "
            'href="%24IMS-CC-FILEBASE%24/QuizImages/fractal.jpg?canvas_download=1" '
            'target="_blank">Fractal Image</a></p>\n'
            "</body>\n</html>\n"
        },
    )

    assert cartridge.get_resource_content("resource_6_wiki_content") == (
        "html",
        {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_6_wiki_content"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="%24WIKI_REFERENCE%24/pages/wiki_content">Wiki Content</a>'
            "\n</body>\n</html>\n"
        },
    )

    assert cartridge.get_resource_content("resource_7_canvas_content") == (
        "html",
        {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_7_canvas_content"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="%24CANVAS_OBJECT_REFERENCE%24/quizzes/abc">Canvas Content</a>'
            "\n</body>\n</html>\n"
        },
    )

    assert cartridge.get_resource_content("resource_module-|-introduction") == (
        "html",
        {
            "html": '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
            "<title>Vertical</title>\n"
            '<meta name="identifier" content="resource_module-|-introduction"/>\n'
            '<meta name="editing_roles" content="teachers"/>\n'
            '<meta name="workflow_state" content="active"/>\n'
            "</head>\n<body>\n"
            '<p>Lorem ipsum...</p>\n<a href="%24WIKI_REFERENCE%24/pages/wiki_content">Wiki Content</a>'
            "\n</body>\n</html>\n"
        },
    )

    assert cartridge.get_resource_content("resource_10_video") == (
        "html",
        {
            "html": '<p><iframe src="https://www.youtube.com/embed/zE-a5eqvlv8" width="727" '
                    'height="409" frameborder="0" allowfullscreen=""></iframe></p>'
        },
    )

    assert cartridge.get_resource_content("resource_6_image_file") == (
        "html",
        {
            "html": '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/></head>'
            '<body><p><img src="/static/CREADOR.png" alt="CREADOR.png"></p></body></html>'
        },
    )
