import zipfile

from pathlib import Path

from cc2olx.models import Cartridge, ResourceFile


def test_cartridge_initialize(imscc_file, settings):
    """
    Tests, that ``Cartridge`` initializes without errors.
    """

    cartridge = Cartridge(imscc_file, settings)

    assert cartridge.normalized is None
    assert cartridge.resources is None

    assert isinstance(cartridge.cartridge, zipfile.ZipFile)
    assert cartridge.file_path == imscc_file


def test_load_manifest_extracted(imscc_file, settings, temp_workspace_dir):
    """
    Tests, that all resources and metadata are loaded fine.
    """

    cartridge = Cartridge(imscc_file, settings)
    cartridge.load_manifest_extracted()

    cartridge_version = "1.3.0"

    assert cartridge.version == cartridge_version
    assert cartridge.directory == Path(temp_workspace_dir) / "output" / imscc_file.stem

    assert cartridge.metadata["schema"] == {
        "name": "IMS Common Cartridge", "version": cartridge_version
    }

    assert len(cartridge.resources) == 2
    assert len(cartridge.resources[0]["children"]) == 5
    assert isinstance(cartridge.resources[0]["children"][0], ResourceFile)


def test_cartridge_normalize(imscc_file, settings):
    cartridge = Cartridge(imscc_file, settings)
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    assert cartridge.normalized == {
        "children": [],
        "identifier": "org_1",
        "structure": "rooted-hierarchy"
    }


def test_cartridge_get_resource_content(imscc_file, settings):
    cartridge = Cartridge(imscc_file, settings)
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    assert cartridge.get_resource_content('i8bf41876741cf5632cff28d3f062b798') == (
        'html',
        {
            'html': "Unimported content: type = 'associatedcontent/imscc_xmlv1p1/learning-application-resource', "
                    "href = 'course_settings/canvas_export.txt'"
        }
    )

    assert cartridge.get_resource_content('i21fcf1e322b1d8263285fb6012b2b46c') == (
        'html',
        {
            'html': '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
                    '<title>Our Purpose</title>\n'
                    '<meta name="identifier" content="i21fcf1e322b1d8263285fb6012b2b46c"/>\n'
                    '<meta name="editing_roles" content="teachers"/>\n<meta name="workflow_state" content="active"/>\n'
                    '</head>\n<body>\n\n</body>\n</html>\n'
        }
    )
