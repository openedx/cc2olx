from glob import glob
from os.path import basename, splitext

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

setup(
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
    description=(
        "Command line tool, that converts Common Cartridge "
        "courses to Open edX Studio imports."
    ),
    entry_points={"console_scripts": ["cc2olx=cc2olx.main:main"]},
    install_requires=[],
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
    version="0.1.0",
    zip_safe=False,
)
