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


def parse_options(args):
    """
    Parses script options from argparse arguments.
    """
    input_files = _get_files(args)

    return {
        "input_files": input_files,
        "output_format": args.result,
        "log_level": args.loglevel,
        "workspace": Path.cwd() / args.output,
        "link_file": args.link_file,
        "passport_file": args.passport_file,
        "relative_links_source": args.relative_links_source,
        "content_types_with_custom_blocks": args.content_types_with_custom_blocks,
    }
