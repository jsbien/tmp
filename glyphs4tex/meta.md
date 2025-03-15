The script glyphs2meta.py is an extension of glyphidx2tex, however it
takes one argument more called <dsed directory>

For every graphic file in the input directory a single line (not
counting the header) CSV file in the output directory is created, with
the same basename but the extension "csv", with the content specified
below.

The metadata file is loaded as before, but the second column values is
stored as dsed.

The input files names are parsed and sorted as before.

