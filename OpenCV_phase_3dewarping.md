The name of the script is PT_dewarp.py.  It takes an obligatory
argument: the path to the direcoty containing the files to be
processed.

The directory contains about 100 files. The files are binary in the
TIFF format, only some of them needs dewarping, it is the task of the
script to regnize them.

The results are stored in the new files (the format can be changed to
PNG if it helps), named by adding a postfix to the base name: "W"
means the file was dewarped, "w" means the file was not changed and is
just a copy of the input file.

A log should be created named PT_dewarp.log containing some basic
information about the script execution.
