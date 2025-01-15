import pytest

from cc2olx.external.canvas import ModuleMeta


@pytest.fixture(scope="session")
def module_meta(fixtures_data_dir):
    """
    Fixture for ModuleMeta object
    """
    module_meta_path = fixtures_data_dir / "imscc_files" / "main" / "course_settings" / "module_meta.xml"
    module_meta = ModuleMeta(module_meta_path)
    return module_meta


def test_external_tool_data_has_url(module_meta):
    """
    Tests that external tool data contains url
    """
    expected = "https://example.com/lit/launch/content_id"
    data = module_meta.get_external_tool_item_data("external_tool")
    actual = data["url"]
    assert expected == actual
