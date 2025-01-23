from unittest.mock import Mock

import pytest

from cc2olx.exceptions import QtiError
from cc2olx.olx_generators import QtiOlxGenerator


class TestQtiOlxGenerator:
    @pytest.mark.parametrize("cc_profile", ["unknown_profile", "cc.chess.v0p1", "cc.drag_and_drop.v0p1", "123"])
    def test_create_nodes_raises_qti_error_if_cc_profile_is_unknown(self, cc_profile):
        generator = QtiOlxGenerator(Mock())

        with pytest.raises(QtiError) as exc_info:
            generator.create_nodes([{"cc_profile": cc_profile}])

        assert str(exc_info.value) == f'Unknown cc_profile: "{cc_profile}"'
