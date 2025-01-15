import pytest

from cc2olx.content_processors import QtiContentProcessor
from cc2olx.content_processors.qti import QtiError
from cc2olx.models import Cartridge


class TestQtiContentProcessor:
    def test_error_is_raised_during_unknown_qti_type_processing(
        self,
        corner_cases_imscc,
        temp_workspace_path,
        empty_content_processor_context,
    ):
        cartridge = Cartridge(corner_cases_imscc, temp_workspace_path)
        cartridge.load_manifest_extracted()
        cartridge.normalize()
        processor = QtiContentProcessor(cartridge, empty_content_processor_context)
        idref = "unknown_qti_assessment_content"
        resource = cartridge.define_resource(idref)

        with pytest.raises(QtiError) as exc_info:
            processor.process(resource, idref)

        assert str(exc_info.value) == 'Unknown cc_profile: "cc.strange.v0p1"'
