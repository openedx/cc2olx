import os
import re

from glob import glob
from os.path import basename, splitext

from setuptools import setup, find_packages


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

    Requirements will include any constraints from files specified
    with -c in the requirements files.
    Returns a list of requirement strings.
    """

    def check_name_consistent(package):
        """
        Raise exception if package is named different ways.

        This ensures that packages are named consistently so we can match
        constraints to packages. It also ensures that if we require a package
        with extras we don't constrain it without mentioning the extras (since
        that too would interfere with matching constraints.)
        """
        canonical = package.lower().replace("_", "-").split("[")[0]
        seen_spelling = by_canonical_name.get(canonical)
        if seen_spelling is None:
            by_canonical_name[canonical] = package
        elif seen_spelling != package:
            raise Exception(
                f'Encountered both "{seen_spelling}" and "{package}" in requirements '
                "and constraints files; please use just one or the other."
            )

    def add_version_constraint_or_raise(current_line, current_requirements, add_if_not_present):
        if regex_match := requirement_line_regex.match(current_line):
            package = regex_match.group(1)
            version_constraints = regex_match.group(2)
            check_name_consistent(package)
            existing_version_constraints = current_requirements.get(package, None)
            # It's fine to add constraints to an unconstrained package,
            # but raise an error if there are already constraints in place.
            if existing_version_constraints and existing_version_constraints != version_constraints:
                raise Exception(
                    f"Multiple constraint definitions found for {package}:"
                    f' "{existing_version_constraints}" and "{version_constraints}".'
                    f"Combine constraints into one location with {package}"
                    f"{existing_version_constraints},{version_constraints}."
                )
            if add_if_not_present or package in current_requirements:
                current_requirements[package] = version_constraints

    by_canonical_name = {}  # e.g. {"django": "Django", "confluent-kafka": "confluent_kafka[avro]"}
    requirements = {}
    constraint_files = set()

    # groups "pkg<=x.y.z,..." into ("pkg", "<=x.y.z,...")
    re_package_name_base_chars = r"a-zA-Z0-9\-_."  # chars allowed in base package name
    # Two groups: name[maybe,extras], and optionally a constraint
    requirement_line_regex = re.compile(
        rf"([{re_package_name_base_chars}]+(?:\[[{re_package_name_base_chars},\s]+\])?)([<>=][^#\s]+)?"
    )

    # Read requirements from .in files and store the path to any
    # constraint files that are pulled in.
    for path in requirements_paths:
        with open(path) as reqs:
            for line in reqs:
                if is_requirement(line):
                    add_version_constraint_or_raise(line, requirements, True)
                if line and line.startswith("-c") and not line.startswith("-c http"):
                    constraint_files.add(os.path.dirname(path) + "/" + line.split("#")[0].replace("-c", "").strip())

    # process constraint files: add constraints to existing requirements
    for constraint_file in constraint_files:
        with open(constraint_file) as reader:
            for line in reader:
                if is_requirement(line):
                    add_version_constraint_or_raise(line, requirements, False)

    # process back into list of pkg><=constraints strings
    return [f'{pkg}{version or ""}' for (pkg, version) in sorted(requirements.items())]


with open("README.rst", encoding="utf-8") as readme_file:
    readme = readme_file.read()

VERSION = get_version("src", "cc2olx", "__init__.py")


setup(
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.2",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
    description="Command line tool, that converts Common Cartridge courses to Open edX Studio imports.",
    entry_points={"console_scripts": ["cc2olx=cc2olx.main:main"]},
    install_requires=load_requirements("requirements/base.in"),
    license="GNU Affero General Public License",
    long_description=readme,
    include_package_data=True,
    keywords="cc2olx",
    name="cc2olx",
    package_dir={"": "src"},
    packages=find_packages("src"),
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    setup_requires=[],
    test_suite="tests",
    tests_require=[],
    url="https://github.com/openedx/cc2olx",
    version=VERSION,
    zip_safe=False,
)
