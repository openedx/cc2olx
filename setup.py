from glob import glob
from os.path import basename, splitext

from setuptools import setup, find_packages

from utils import get_version, load_requirements

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
        "Topic :: Utilities",
    ],
    description="Command line tool, that converts Common Cartridge courses to Open edX Studio imports.",
    entry_points={"console_scripts": ["cc2olx=cc2olx.script:run_script"]},
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
