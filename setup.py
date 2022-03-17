import os
import re

from glob import glob
from os.path import basename, splitext

from setuptools import setup, find_packages

with open("README.rst", encoding="utf-8") as readme_file:
    readme = readme_file.read()


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


VERSION = get_version("src", "cc2olx", "__init__.py")


setup(
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
    description=("Command line tool, that converts Common Cartridge " "courses to Open edX Studio imports."),
    entry_points={"console_scripts": ["cc2olx=cc2olx.main:main"]},
    install_requires=["lxml"],
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
    url="https://github.com/edx/cc2olx",
    version=VERSION,
    zip_safe=False,
)
