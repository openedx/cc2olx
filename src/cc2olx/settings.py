import argparse
import logging
import os


RESULT_TYPE_FOLDER = 'folder'
RESULT_TYPE_ZIP = "zip"

logging.basicConfig(
    level=logging.DEBUG,
    format='{%(filename)s:%(lineno)d} - %(message)s',
)
logger = logging.getLogger()


def _parse_args():
    parser = argparse.ArgumentParser(
        description='This script converts imscc files into folders with all the content; in the defined folder structure.'
    )
    group = parser.add_mutually_exclusive_group(
        required=True,
    )
    group.add_argument(
        '-f',
        '--file',
        nargs=1,
        help='Please provide the path to the imscc file.',
    )
    group.add_argument(
        '-l',
        '--list',
        nargs='*',
        help='Please provide the paths to a list of imscc files.',
    )
    group.add_argument(
        '-d',
        '--dir',
        nargs=1,
        help='Please provide the path to the directory containing imscc file(s).',
    )
    parser.add_argument(
        '-ll',
        '--loglevel',
        nargs=1,
        choices=[
            'DEBUG',
            'INFO',
            'WARNING',
            'ERROR',
            'CRITICAL',
        ],
        help='Please provide the appropriate level to change the detail of logs. It can take one of the following values, DEBUG, INFO, WARNING, ERROR, CRITICAL as argument.',
    )
    parser.add_argument(
        '-r',
        '--result',
        nargs=1,
        choices=[
            RESULT_TYPE_FOLDER,
            RESULT_TYPE_ZIP,
        ],
        default=RESULT_TYPE_FOLDER,
        help="Please provide the way in which final result has to be. It can take one of the following values, {folder}, {zip} as argument.".format(
            folder=RESULT_TYPE_FOLDER,
            zip=RESULT_TYPE_ZIP,
        ),
    )
    args = parser.parse_args()
    return args


def _get_files(args):
    input_files = []
    if args.file:
        input_files.extend(args.file)
    elif args.list:
        input_files.extend(args.list)
    elif args.dir:
        path_folder = ''.join(args.dir)
        for input_file in os.listdir(path_folder):
            if input_file.endswith('.imscc'):
                input_file_full = os.path.join(path_folder, input_file)
                input_files.append(input_file_full)
    return input_files


def _get_log_level(args):
    log_level = 'INFO'
    if args.loglevel:
        log_level = ''.join(args.loglevel)
    return log_level


def _get_input(args):
    result_type = ''
    if args.result:
        result_type = ''.join(args.result)
    return result_type


def collect_settings():
    args = _parse_args()
    input_files = _get_files(args)
    log_level = _get_log_level(args)
    output_format = _get_input(args)
    dir_path = os.path.dirname(os.path.abspath(__file__))
    temp_folder_name = 'tmp'
    workspace = os.path.join(dir_path, '../..', temp_folder_name)
    workspace = os.path.normpath(workspace)
    logging_config = {
        'level': log_level,
        'format': '{%(filename)s:%(lineno)d} - %(message)s',
    }
    settings = {
        'input_files': input_files,
        'output_format': output_format,
        'logging_config': logging_config,
        'workspace': workspace,
    }
    return settings
