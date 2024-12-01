find_edited.py

One argument: directory name

Iterate over *.log files in the subdirectories of the argument.
Every file has a time stamp as its last line.

List and count the file names of the logs which have the modification
time later than the creation time stamp. The list should be sorted
alphabetically.

At the end of the run print the total number of the files.

An example of a log file:

--- cut here ---
Arguments: input_file=masks/m02.tiff, djvu_file=Augezdecki-01a_PT08_403.djvu, output_directory=02
1: 10
2: 33 14+15

Invalid strips (no letterboxes):
Timestamp: 2024-11-30T12:54:30.742281
--- cut here ---


