from cc2olx.content_processors.utils import WebContentFile


class TestWebContentFile:
    def test_resource_relative_path_is_defined_correctly(self, resource_pdf_1_web_content_file):
        assert resource_pdf_1_web_content_file.resource_relative_path == "web_resources/PEP_8.pdf"

    def test_resource_file_path_is_defined_correctly(self, resource_pdf_1_web_content_file, temp_workspace_path):
        expected_path = temp_workspace_path / "output/course/web_resources/PEP_8.pdf"

        assert resource_pdf_1_web_content_file.resource_file_path == expected_path

    def test_static_file_path_from_web_resources_dir_is_defined_correctly(self, resource_pdf_1_web_content_file):
        assert resource_pdf_1_web_content_file.static_file_path == "PEP_8.pdf"

    def test_static_file_path_outside_web_resources_dir_is_defined_correctly(self, cartridge):
        resource = cartridge.define_resource("resource_pdf_2")
        web_content_file = WebContentFile(cartridge, resource["children"][0])

        assert web_content_file.static_file_path == "extra_files/example.pdf"

    def test_olx_static_path_is_defined_correctly(self, resource_pdf_1_web_content_file):
        assert resource_pdf_1_web_content_file.olx_static_path == "/static/PEP_8.pdf"

    def test_it_is_detected_that_web_content_file_is_from_web_resources_dir(self, resource_pdf_1_web_content_file):
        assert resource_pdf_1_web_content_file.is_from_web_resources_dir() is True

    def test_it_is_detected_that_web_content_file_is_outside_web_resources_dir(self, cartridge):
        resource = cartridge.define_resource("resource_pdf_2")
        web_content_file = WebContentFile(cartridge, resource["children"][0])

        assert web_content_file.is_from_web_resources_dir() is False
