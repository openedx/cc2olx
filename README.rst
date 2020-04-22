cc2olx
######

A hackathon project to explore importing Common Cartridge courses into Open edX
Studio.

This is the result of a few days of work.  It converts Common Cartridge .imscc
files into .tar.gz files that can be imported into Studio. It is not
production-ready, but it is a starting point for more development.


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


Use
---

The converter is a command-line Python 3 program.

To convert one file::

    ./bin/run -f <IMSCC_FILE>

This will write a .tar.gz file into the tmp directory here.


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
