# flake8: noqa: E501

import os
import textwrap
import zipfile

from pathlib import Path

import pytest

from cc2olx.cli import parse_args
from cc2olx.models import Cartridge
from cc2olx.settings import collect_settings


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

    os.chdir(old_working_dir)


@pytest.fixture(scope="session")
def imscc_data():
    """
    This fixture is a dict, where each key-value
    pair represents file from simple ``.imscc`` file.
    """

    return {
        "imsmanifest.xml": textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <manifest identifier="i5eb2366c5fc27e17b7bcb0ae4b0a9c0b" xmlns="http://www.imsglobal.org/xsd/imsccv1p3/imscp_v1p1" xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p3/LOM/resource" xmlns:lomimscc="http://ltsc.ieee.org/xsd/imsccv1p3/LOM/manifest" xmlns:cpx="http://www.imsglobal.org/xsd/imsccv1p3/imscp_extensionv1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://ltsc.ieee.org/xsd/imsccv1p3/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p3/LOM/ccv1p3_lomresource_v1p0.xsd http://www.imsglobal.org/xsd/imsccv1p3/imscp_v1p1 http://www.imsglobal.org/profile/cc/ccv1p3/ccv1p3_imscp_v1p2_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p3/LOM/manifest http://www.imsglobal.org/profile/cc/ccv1p3/LOM/ccv1p3_lommanifest_v1p0.xsd http://www.imsglobal.org/xsd/imsccv1p3/imscp_extensionv1p2 http://www.imsglobal.org/profile/cc/ccv1p3/ccv1p3_cpextensionv1p2_v1p0.xsd">
              <metadata>
                <schema>IMS Common Cartridge</schema>
                <schemaversion>1.3.0</schemaversion>
                <lomimscc:lom>
                  <lomimscc:general>
                    <lomimscc:title>
                      <lomimscc:string>The Life of Paul</lomimscc:string>
                    </lomimscc:title>
                  </lomimscc:general>
                  <lomimscc:lifeCycle>
                    <lomimscc:contribute>
                      <lomimscc:date>
                        <lomimscc:dateTime>2018-09-13</lomimscc:dateTime>
                      </lomimscc:date>
                    </lomimscc:contribute>
                  </lomimscc:lifeCycle>
                  <lomimscc:rights>
                    <lomimscc:copyrightAndOtherRestrictions>
                      <lomimscc:value>yes</lomimscc:value>
                    </lomimscc:copyrightAndOtherRestrictions>
                    <lomimscc:description>
                      <lomimscc:string>Public Domain - http://en.wikipedia.org/wiki/Public_domain</lomimscc:string>
                    </lomimscc:description>
                  </lomimscc:rights>
                </lomimscc:lom>
              </metadata>
              <organizations>
                <organization identifier="org_1" structure="rooted-hierarchy">
                  <item identifier="LearningModules">
                  </item>
                </organization>
              </organizations>
              <resources>
                <resource identifier="i8bf41876741cf5632cff28d3f062b798" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" href="course_settings/canvas_export.txt">
                  <file href="course_settings/module_meta.xml"/>
                  <file href="course_settings/assignment_groups.xml"/>
                  <file href="course_settings/files_meta.xml"/>
                  <file href="course_settings/media_tracks.xml"/>
                  <file href="course_settings/canvas_export.txt"/>
                </resource>
                <resource identifier="i21fcf1e322b1d8263285fb6012b2b46c" type="webcontent" href="wiki_content/our-purpose.html">
                  <file href="wiki_content/our-purpose.html"/>
                </resource>
              </resources>
            </manifest>
        """),
        "wiki_content/our-purpose.html": textwrap.dedent("""\
            <html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
            <title>Our Purpose</title>
            <meta name="identifier" content="i21fcf1e322b1d8263285fb6012b2b46c"/>
            <meta name="editing_roles" content="teachers"/>
            <meta name="workflow_state" content="active"/>
            </head>
            <body>

            </body>
            </html>
        """),
        "course_settings/assignment_groups.xml": textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <assignmentGroups xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
            </assignmentGroups>
        """),
        "course_settings/canvas_export.txt": textwrap.dedent("""\
            Q: What did the panda say when he was forced out of his natural habitat?
            A: This is un-BEAR-able
        """),
        "course_settings/files_meta.xml": textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <fileMeta xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
            </fileMeta>
        """),
        "course_settings/media_tracks.xml": textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <media_tracks xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
            </media_tracks>
        """),
        "course_settings/module_meta.xml": textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <modules xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
            </modules>
        """),
    }


@pytest.fixture(scope="session")
def imscc_file(temp_workspace_dir, imscc_data):
    """
    Creates ``.imscc`` file from ``imscc_data`` fixture.
    """

    imscc_file_path = Path(temp_workspace_dir) / "single-page.imscc"
    with zipfile.ZipFile(imscc_file_path, "w") as zf:
        for xml_document_path, xml_document_content in imscc_data.items():
            zf.writestr(xml_document_path, xml_document_content)

    return imscc_file_path


@pytest.fixture
def settings(imscc_file):
    """
    Basic settings fixture.
    """

    parsed_args = parse_args(["-i", str(imscc_file)])
    return collect_settings(parsed_args)


@pytest.fixture
def cartridge(imscc_file, settings):
    cartridge = Cartridge(imscc_file, settings)
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    return cartridge
