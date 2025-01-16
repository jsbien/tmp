The name of the script is PT_glyphs.py.  It takes an obligatory
argument: the path to the directory containing the files to be
processed.

The directory contains about 100 subdirectories containing graphic
files with lines of text. The files are binary in the TIFF format.

For every file in a subdirectory a new subdirectory is created named
with the parent directory basename postfixed with "_glyphs".

Than the files is split into glyphs which are is stored in the
appropriate subdirectory in a separate file named with the basename of
the processed file prefixed by two digit glyph number and the
underscore.

In most cases the glyphs can be separated by a vertical cut, but
sometimes the cut has to be done with an appropriate polygonal chain.

In all cases the final glyph image should be rectangular.

The glyphs never touch as we are working on font tables, not real
texts.

A log should be created named PT_glyphs_<time_stamp>.py contaning the
script version, the coordinates of the bounding boxess of the
recognized glyphs, some information about the cut used to separate the
glyphs and the number of glyphs in the line. The intention is to check
the logs for possible regression bugs.

polygonal chainx1
