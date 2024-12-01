# Introduction #

I have reviewed the output of `segment-all` and noticed a lot of
speckles recognized erroneusly as characters. I have marked them by
hand in the log files and in this phase we will convert my notes to
the form suitable for further processing. This means:

1. the relevant log files will be edited and new version created with
the new time-stamp

2. speckles images will be copied to the a separate directory for
additional inspection

3. speckles information will be retrieved from the appropriate CVS
   files and copies to new CVS file.

I have made also other notes in the log file which for the time being
should be just preserved.

# Script specification #

The Python script is to be named `collect-specles.py`, it takes one
argument in the form of a directory name.

In this directory a subdirectory `speckles` is to be created. It will
contain the index `speckles.csv` and the speckles image files.

The subdirectories of the argument directory are searched for log
files containing at least one `-` character. The list of the logs
found is sorted alphabetically, then for every log the following
operations are be performed.

## Actions for a specific log file ##

First, the context of the `-` character is to be analized as we have
two types of speckle identifiers. `-` can preceed a number or the
letter `l`. The constructs `-<number>` may occur several times in a
line with or without the spaces between them. Here are some examples:

    1: 1 -l
	1: 30 -22-24
    3: 44 -38

If the log contains both `-l` and `-<number>`, we start processing with
`-<number`. The number refers to the letterbox in th specified
line. 

### Actions for a specific numeric speckle identifier ###

Hence `-38` in the line `3: 44 -38` in the log
`m01-2024-11-30-12-54.log` refers to the file
`m01.tiff_line_003_box_038.png` in the same directory, the file is to be
moved to the `speckles` directory mentioned above.
Additionally it refers to the line

    001 l 3 b 38;file:Augezdecki-01_PT08_402.djvu?djvuopts=&page=1&highlight=2178,571,2,115;Augezdecki-01_PT08_402 l 3 b 38; ※

in the file `Augezdecki-01_PT08_402.csv`. This line is to be appended to the `speckles.csv` file mentioned above.

Last but not least, a new log is be written with the speckle identifier place in brackets:

    3: 44 [-38]

### Actions for a speckle line identifier ###

The note `-l` means the line is either just a speckle or contains only
speckles. Let's illustrate it with an example of the following
fragment of a log

	Arguments: input_file=masks/m03.tiff, djvu_file=Augezdecki-01b_PT08_404.djvu, output_directory=03

     1: 1 -l
     2: 23
     3: 1

We move to the `speckles` directory all the files
`m03.tiff_line_001_*.png` and we append to `speckles.csv` all the
lines from `Augezdecki-01b_PT08_404.csv` starting with `003 l
1`. Moreover we have to renumerate lines in the log placing old
numbers in the brackets; we place also in brackets the whole line
containg `-l`. So the new log will contain

	Arguments: input_file=masks/m03.tiff, djvu_file=Augezdecki-01b_PT08_404.djvu, output_directory=03

[1: 1 -l]
    1 [2]: 23
    2 [3]: 1

