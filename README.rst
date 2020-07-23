cc2olx
######

*cc2olx* is a converter of `Common Cartridge <https://www.imsglobal.org/activity/common-cartridge>`_ `.imscc` files into `.tar.gz` files that can be imported into Studio.

What is supported
-----------------

Converted:

- HTML
- Web links
- Some videos
- LTI links

Not converted:

- Images
- QTI assessments


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
