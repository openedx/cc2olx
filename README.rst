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
---

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

To Do
-----

We would love help building out this tool.  If you can help, either with
development, or with real-world testing, please get in touch: ned@edx.org.

Work that needs to be done:

- Test on real courses
- Clean up the code
- Write tests
- Package in a way that more people will be able to run it
- Add support for more Common Cartridge content
- Write more documentation
