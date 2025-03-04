cc2olx
######

.. image:: https://github.com/openedx/cc2olx/workflows/Python%20CI/badge.svg?branch=master
    :target: https://github.com/openedx/cc2olx/actions?query=workflow%3A%22Python+CI%22

*cc2olx* is a converter of `Common Cartridge <https://www.imsglobal.org/activity/common-cartridge>`_ `.imscc` files into `.tar.gz` files that can be imported into Studio.

What is supported
-----------------

Converted:

- HTML
- Web links
- Some videos
- LTI links
- QTI assessments
- Assignments

Not converted:

- Images


Install
-------

Clone repository and install via setup.py::

    python setup.py install

Use
---

The converter is a command-line Python 3 program.

To convert one file::

    cc2olx -i <IMSCC_FILE>

This will write a `.tar.gz` file into the tmp directory here.

To store all results in `zip` file::

    cc2olx -r zip -i <IMSCC_FILE>

An embeded video in an iframe tag in HTML can be converted to it's
corresponding video xblock if we provide a link map file to it.

The CSV file should have the following header::

    External Video Link, Edx Id, Youtube Id

Either Edx Id or Youtube Id should be be present.
In case both of these are given Edx Id takes priority.

The link map file can be supplied using `-f` or `--link_file`::

    cc2olx -r zip -i <IMSCC_FILE> -f <CSV_FILE>

If the original course content contains relative links and the resources
(images, documents etc) the links point to are not included into the exported
course dump, you can specify their source using `-s` flag:

    cc2olx -i <IMSCC_FILE> -s <RELATIVE_LINKS_SOURCE>

Dockerization
-------------

To make the application platform-independent, it is dockerized. To run the
application using Docker you need:

1. Build the image::

    docker build -t cc2olx .

2. Run the conversion command in a container by mounting passed argument path
directories/files and passing the corresponding arguments to the script::

    docker run --rm -v /input/file/path/cc_course_dump.imscc:/data/input/cc_course_dump.imscc -v /output/file/path/output_dir:/data/output/ cc2olx -r zip -i /data/input/cc_course_dump.imscc -o /data/output/edx_dump

It will convert Common Cartridge dump from */input/file/path/cc_course_dump.imscc*
and save the OLX in */output/file/path/output_dir/edx_dump.zip* file.

Test Data
---------

There are some test imscc files in `test_data` directory, but if you can also try **cc2olx** on some larger courses:

- `HBUHSD Geometry Resource Course <https://s3.amazonaws.com/public-imscc/c075c6df1f674a7b9d9192307e812f74.imscc>`_ (29.7 MB) (Kendra Rosales, by-nc-sa 4.0, `source <https://lor.instructure.com/resources/c075c6df1f674a7b9d9192307e812f74>`_)
- `Kung Fu Canvas <https://s3.amazonaws.com/public-imscc/faa3332ffd834070ad81d97bdb236649.imscc>`_ (65.48 MB) (Mike Cowen, by-nc-sa 4.0, `source <https://lor.instructure.com/resources/faa3332ffd834070ad81d97bdb236649>`_)
- `KNOW & The Challenge Mosaic <https://s3.amazonaws.com/public-imscc/d933c048da6d4fd5a9cb552148d628cb.imscc>`_ (572.43 MB) (Missy Widmann, by-nc-sa 4.0, `source <https://lor.instructure.com/resources/d933c048da6d4fd5a9cb552148d628cb>`_)

To Do
-----

We would love help building out this tool.  If you can help, either with
development, or with real-world testing, please submit pull request or open new issue.

Work that needs to be done:

- Test on real courses
- Clean up the code
- Add support for more Common Cartridge content
- Write more documentation

Video Upload Tool
#################

- The *cc2olx* repository also has a video upload tool that can be used to upload videos to directly to edX's video encoding pipeline. See the tool's README :ref:`video_upload_tool`. for a further details.
