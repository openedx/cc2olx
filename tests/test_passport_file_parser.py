from cc2olx.utils import passport_file_parser


def test_parser_warns_on_missing_header(bad_passports_csv, caplog):
    passports = passport_file_parser(bad_passports_csv)

    assert [rec.levelname for rec in caplog.records] == ["WARNING"]
    assert [rec.message for rec in caplog.records] == [
        "Ignoring passport file (%s). Please ensure that the file"
        " contains required headers consumer_id, consumer_key and consumer_secret." % bad_passports_csv
    ]
    assert passports == {}


def test_parser_returns_correct_dict(passports_csv, caplog):
    passports = passport_file_parser(passports_csv)

    # assert there are no warning logs
    assert [rec.message for rec in caplog.records] == []
    assert passports == {
        "codio": "codio:my_codio_key:my_codio_secret",
        "lti_tool": "lti_tool:my_consumer_key:my_consumer_secret_key",
        "external_tool_lti": "external_tool_lti:external_tool_lti_key:external_tool_lti_secret",
        "smart_quiz": "smart_quiz:smart_quiz_key:smart_quiz_secret",
    }
