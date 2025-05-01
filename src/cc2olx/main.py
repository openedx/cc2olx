import logging
import shutil
import tempfile
from contextlib import nullcontext
from pathlib import Path
from typing import Optional, Set

from cc2olx import filesystem, olx
from cc2olx.cli import parse_args, RESULT_TYPE_FOLDER, RESULT_TYPE_ZIP
from cc2olx.constants import OLX_STATIC_DIR
from cc2olx.logging import build_console_logger, build_input_processing_file_logger
from cc2olx.models import Cartridge
from cc2olx.parser import InputFileCollectingResult, parse_options
from cc2olx.utils import build_default_exception_output

console_logger = build_console_logger(__name__)


def convert_one_file(
    input_file,
    workspace,
    link_file=None,
    passport_file=None,
    relative_links_source=None,
    content_types_with_custom_blocks=None,
    logs_dir_path=None,
):
    content_types_with_custom_blocks = content_types_with_custom_blocks or []

    filesystem.create_directory(workspace)

    cartridge = Cartridge(input_file, workspace)
    cartridge.load_manifest_extracted()
    cartridge.normalize()

    olx_export = olx.OlxExport(
        cartridge,
        link_file,
        passport_file,
        relative_links_source,
        content_types_with_custom_blocks,
        logs_dir_path,
    )
    olx_filename = cartridge.directory.parent / (cartridge.directory.name + "-course.xml")
    policy_filename = cartridge.directory.parent / "policy.json"

    with open(str(olx_filename), "w", encoding="utf-8") as olxfile:
        olxfile.write(olx_export.xml())

    with open(str(policy_filename), "w", encoding="utf-8") as policy:
        policy.write(olx_export.policy())

    tgz_filename = (workspace / cartridge.directory.name).with_suffix(".tar.gz")

    file_list = [
        (str(olx_filename), "course.xml"),
        (str(policy_filename), "policies/course/policy.json"),
        (str(cartridge.directory / "web_resources"), "/{}/".format(OLX_STATIC_DIR)),
    ]

    # Add static files that are outside of web_resources directory
    file_list += [
        (str(cartridge.directory / original_filepath), olx_static_path)
        for olx_static_path, original_filepath in cartridge.olx_to_original_static_file_paths.extra.items()
    ]

    filesystem.add_in_tar_gz(str(tgz_filename), file_list)

    return olx_export.export_statistics


def main():
    args = parse_args()
    options = parse_options(args)

    workspace = options["workspace"]
    link_file = options["link_file"]
    passport_file = options["passport_file"]
    relative_links_source = options["relative_links_source"]
    content_types_with_custom_blocks = options["content_types_with_custom_blocks"]
    logs_dir_path = options["logs_dir_path"]

    # setup root logger
    logging.getLogger().setLevel(options["log_level"])

    with tempfile.TemporaryDirectory() as temp_workspace_dirname:
        with tempfile.TemporaryDirectory() if logs_dir_path else nullcontext() as temp_logs_dirname:
            temp_workspace = Path(temp_workspace_dirname) / workspace.stem
            temp_logs_dir_path = Path(temp_logs_dirname) / logs_dir_path.stem if temp_logs_dirname else None

            _log_input_files_collection_failures(options["invalid_input_file_collection_results"], temp_logs_dir_path)

            for input_file in options["input_files"]:
                console_logger.info("The file %s converting is started.", input_file)

                file_logger = build_input_processing_file_logger(
                    __name__,
                    logs_dir_path=temp_logs_dir_path,
                    input_file_path=input_file,
                )

                try:
                    export_statistics = convert_one_file(
                        input_file,
                        temp_workspace,
                        link_file,
                        passport_file,
                        relative_links_source,
                        content_types_with_custom_blocks,
                        temp_logs_dir_path,
                    )
                except Exception as exc:
                    _log_file_converting_failure(input_file, exc, file_logger)
                else:
                    _log_file_converting_success(input_file, export_statistics, file_logger)

            _output_converting_results(options["output_format"], workspace, temp_workspace)
            _output_converting_logs(logs_dir_path, temp_logs_dir_path)

    return 0


def _log_input_files_collection_failures(
    invalid_input_file_collection_results: Set[InputFileCollectingResult],
    temp_logs_dir_path: Optional[Path],
):
    """
    Log the input files collection failure details.
    """
    for file_path, validation_message in invalid_input_file_collection_results:
        file_logger = build_input_processing_file_logger(
            __name__,
            logs_dir_path=temp_logs_dir_path,
            input_file_path=file_path,
        )

        console_logger.error(validation_message)
        file_logger.error(validation_message)


def _log_file_converting_failure(input_file: Path, exception: Exception, file_logger: logging.Logger) -> None:
    """
    Log the file converting failure details.
    """
    console_logger.error("Error while converting %s file:", input_file)
    console_logger.exception(exception)

    file_logger.error('The file converting if failed: "%s".', build_default_exception_output(exception))


def _log_file_converting_success(
    input_file: Path,
    export_statistics: olx.OlxExportStatistics,
    file_logger: logging.Logger,
) -> None:
    """
    Log the file converting success details.
    """
    processed_blocks_message = f"Successfully processed blocks count: {export_statistics.success_count}."
    not_processed_blocks_message = f"Not processed blocks count: {export_statistics.failure_count}."

    console_logger.info("The file %s converting is finished.", input_file)
    console_logger.info(processed_blocks_message)
    console_logger.info(not_processed_blocks_message)

    file_logger.info("The file converting is finished.")
    file_logger.info(processed_blocks_message)
    file_logger.info(not_processed_blocks_message)


def _output_converting_results(output_format: str, workspace: Path, temp_workspace: Path) -> None:
    """
    Write the exported files to the output directory.
    """
    if temp_workspace.exists():
        if output_format == RESULT_TYPE_FOLDER:
            shutil.rmtree(str(workspace), ignore_errors=True)
            shutil.copytree(str(temp_workspace), str(workspace))
        elif output_format == RESULT_TYPE_ZIP:
            shutil.make_archive(str(workspace), "zip", str(temp_workspace))


def _output_converting_logs(logs_dir_path: Optional[Path], temp_logs_dir_path: Optional[Path]) -> None:
    """
    Write the logs collected during converting to the logs destination directory.
    """
    if temp_logs_dir_path and temp_logs_dir_path.exists():
        shutil.rmtree(str(logs_dir_path), ignore_errors=True)
        shutil.copytree(str(temp_logs_dir_path), str(logs_dir_path))
