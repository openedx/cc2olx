from pathlib import Path
from typing import NamedTuple, Optional

from cc2olx.logging import build_console_logger

COMMON_CARTRIDGE_FILE_EXTENSION = ".imscc"

console_logger = build_console_logger(__name__)


def _is_cartridge_file(path):
    return path.is_file() and path.suffix == COMMON_CARTRIDGE_FILE_EXTENSION


class InputFileCollectingResult(NamedTuple):
    """
    Encapsulate the input file collection result.
    """

    file_path: Path
    validation_message: Optional[str] = None


def _collect_input_files(parsed_args):
    """
    Collects all Common Cartridge files from list of files and directories.
    """
    collection_result = set()

    for path in parsed_args.inputs:
        if not path.exists():
            collection_result.add(InputFileCollectingResult(path, f"File {path} does not exist. Skipped."))
            continue

        if _is_cartridge_file(path):
            collection_result.add(InputFileCollectingResult(path))
        elif path.is_dir():
            for input_file in path.iterdir():
                if _is_cartridge_file(input_file):
                    collection_result.add(InputFileCollectingResult(input_file))
        else:
            collection_result.add(
                InputFileCollectingResult(
                    path,
                    f"File {path} is not a supported Common Cartridge archive. Skipped.",
                )
            )

    return collection_result


def _parse_logs_dir_path(logs_dir: Optional[str]) -> Path:
    """
    Parse the path to the directory for logs storing.
    """
    return Path.cwd() / logs_dir if logs_dir else None


def parse_options(args):
    """
    Parses script options from argparse arguments.
    """
    input_file_collection_results = _collect_input_files(args)
    input_files = {
        collection_results.file_path
        for collection_results in input_file_collection_results
        if collection_results.validation_message is None
    }
    invalid_input_file_collection_results = {
        collection_results
        for collection_results in input_file_collection_results
        if collection_results.validation_message is not None
    }

    return {
        "input_files": input_files,
        "invalid_input_file_collection_results": invalid_input_file_collection_results,
        "output_format": args.result,
        "log_level": args.loglevel,
        "workspace": Path.cwd() / args.output,
        "link_file": args.link_file,
        "passport_file": args.passport_file,
        "relative_links_source": args.relative_links_source,
        "content_types_with_custom_blocks": args.content_types_with_custom_blocks,
        "logs_dir_path": _parse_logs_dir_path(args.logs_dir),
    }
