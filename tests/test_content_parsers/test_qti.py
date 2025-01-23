from unittest.mock import MagicMock, Mock, PropertyMock, call, patch

import pytest

from cc2olx.content_parsers import QtiContentParser
from cc2olx.exceptions import QtiError


class TestQtiContentParser:
    @pytest.mark.parametrize("cc_profile", ["unknown_profile", "cc.chess.v0p1", "cc.drag_and_drop.v0p1", "123"])
    def test_parse_problem_raises_qti_error_if_cc_profile_is_unknown(self, cc_profile):
        parser = QtiContentParser(Mock(), Mock())
        problem_mock = MagicMock(profile=cc_profile)

        with pytest.raises(QtiError) as exc_info:
            parser._parse_problem(problem_mock, Mock(), Mock())

        assert str(exc_info.value) == f'Unknown cc_profile: "{cc_profile}"'

    @patch("cc2olx.content_parsers.qti.logger")
    def test_parse_problem_logs_inability_to_process_problem(self, logger_mock):
        parser = QtiContentParser(Mock(), Mock())
        ident_mock = MagicMock()
        resource_file_path_mock = Mock()
        cc_profile_mock = Mock()
        problem_mock = Mock(profile=cc_profile_mock, attrib={"ident": ident_mock})
        expected_logger_info_call_args_list = [
            call("Problem with ID %s can't be converted.", ident_mock),
            call("    Profile %s is not supported.", cc_profile_mock),
            call("    At file %s.", resource_file_path_mock),
        ]

        with patch(
            "cc2olx.content_parsers.qti.QtiContentParser._problem_parsers_map",
            new_callable=PropertyMock,
        ) as problem_parsers_map_mock:
            problem_parsers_map_mock.return_value = {cc_profile_mock: Mock(side_effect=NotImplementedError)}

            parser._parse_problem(problem_mock, Mock(), resource_file_path_mock)

        assert logger_mock.info.call_count == 3
        assert logger_mock.info.call_args_list == expected_logger_info_call_args_list
