import os
import re


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename, encoding="utf-8").read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string. ")


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement.

    That is, it is not blank, a comment, or editable.
    """
    # Remove whitespace at the start/end of the line
    line = line.strip()

    # Skip blank lines, comments, and editable installs
    return bool(line) and not line.startswith(("-r", "#", "-e", "git+", "-c"))


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.

    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.split("#")[0].strip() for line in open(path).readlines()
            if is_requirement(line)
        )
    return list(requirements)
