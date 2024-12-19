from pathlib import Path

COMMON_CARTRIDGE_FILE_EXTENSION = ".imscc"


def _is_cartridge_file(path):
    return path.is_file() and path.suffix == COMMON_CARTRIDGE_FILE_EXTENSION


def _get_files(parsed_args):
    """
    Collects all Common Cartridge files from list of files and directories.
    """

    files = set()

    for path in parsed_args.inputs:
        if not path.exists():
            raise FileNotFoundError

        if _is_cartridge_file(path):
            files.add(path)

        if path.is_dir():
            for input_file in path.iterdir():
                if _is_cartridge_file(input_file):
                    files.add(input_file)

    return files


def collect_settings(parsed_args):
    """
    Collects settings dictionary from argparse arguments.
    """

    input_files = _get_files(parsed_args)
    log_level = parsed_args.loglevel
    logging_config = {
        "level": log_level,
        "format": "{%(filename)s:%(lineno)d} - %(message)s",
    }
    settings = {
        "input_files": input_files,
        "output_format": parsed_args.result,
        "logging_config": logging_config,
        "workspace": Path.cwd() / parsed_args.output,
        "link_file": parsed_args.link_file,
        "passport_file": parsed_args.passport_file,
        "relative_links_source": parsed_args.relative_links_source,
    }
    return settings
