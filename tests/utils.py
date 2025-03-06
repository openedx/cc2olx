import itertools
import zipfile
from typing import List

import xmlformatter

formatter = xmlformatter.Formatter(compress=True, encoding_output="UTF-8")


def format_xml(xml):
    return formatter.format_string(xml)


def zip_imscc_dir(imscc_dir_path, result_path):
    """
    ZIPs the directory with .imscc content.
    """
    with zipfile.ZipFile(str(result_path), "w") as zf:
        for cc_file in imscc_dir_path.rglob("*"):
            if cc_file.is_file():
                zf.write(str(cc_file), str(cc_file.relative_to(imscc_dir_path)))


def build_multi_value_args(arg_name: str, values: List[str]) -> List[str]:
    """
    Build arguments list for multi-value arguments.
    """
    return list(itertools.chain(*[(arg_name, value) for value in values]))
