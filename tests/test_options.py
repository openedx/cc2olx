from pathlib import Path

from cc2olx.cli import parse_args
from cc2olx.parser import InputFileCollectingResult, parse_options
from .utils import build_multi_value_args


def test_parse_options(imscc_file):
    parsed_args = parse_args(["-i", str(imscc_file)])

    options = parse_options(parsed_args)

    assert options == {
        "input_files": {imscc_file},
        "invalid_input_file_collection_results": set(),
        "output_format": parsed_args.result,
        "workspace": Path.cwd() / "output",
        "link_file": None,
        "passport_file": None,
        "log_level": parsed_args.loglevel,
        "relative_links_source": None,
        "content_types_with_custom_blocks": [],
        "logs_dir_path": None,
    }


def test_invalid_input_files_are_parsed(imscc_file, fixtures_data_dir):
    passport_file_path = fixtures_data_dir / "passports.csv"
    not_existed_file_path = fixtures_data_dir / "not_existed_cc_file.imscc"
    input_files = [str(imscc_file), str(not_existed_file_path), str(passport_file_path)]
    input_args = build_multi_value_args("-i", input_files)
    expected_invalid_input_file_collection_results = {
        InputFileCollectingResult(
            passport_file_path,
            f"File {passport_file_path} is not a supported Common Cartridge archive. Skipped.",
        ),
        InputFileCollectingResult(
            not_existed_file_path,
            f"File {not_existed_file_path} does not exist. Skipped.",
        ),
    }
    parsed_args = parse_args(input_args)

    options = parse_options(parsed_args)

    assert options["invalid_input_file_collection_results"] == expected_invalid_input_file_collection_results


def test_input_directory_option_parsing(fixtures_data_dir):
    misc_dir_path = fixtures_data_dir / "misc"
    expected_input_files = {fixtures_data_dir / "misc" / "empty_cc.imscc"}
    parsed_args = parse_args(["-i", str(misc_dir_path)])

    options = parse_options(parsed_args)

    assert options["input_files"] == expected_input_files
