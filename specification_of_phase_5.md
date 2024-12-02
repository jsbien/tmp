# Introduction #

I have reviewed the output of `segment-all` and noticed a lot of
speckles recognized erroneusly as characters. I have marked them by
hand in the log files and in this phase we will convert my notes to
the form suitable for further processing. This is to be done by a
Python script named `collect-speckles.py`.

I have made also some other notes in the log file which for the time
being should be just preserved.

# Script specification #

## Objective ##
 Process logs to identify speckles and handle them appropriately:
            
  * Update log files with modified content.
  * Move speckle images to a new directory (`speckles`) for further inspection.
  * Append speckle-related data to a new CSV file (`speckles.csv`),
    called later speckle index+.

## Inputs #
  *  A directory name is passed as an argument.
  *  Subdirectories within this directory contain `.log` files to be
     processed. They contain also the index files and so called
     snippets graphic files, which are used by the script in the way
     described below..
	 
## Outputs	 
  *  The output of the script will be placed in the directory passed
as the argument, in the subdirectory `speckles` and the file
`speckles.csv`
  *  Updated logs will be placed in the directory of the original log
  .
##  Processing ##

*        Identify .log files containing speckle identifiers (indicated by "-").

	Search for "-" only in in the proper content of the logs,
    i.e. ignoring the metadata, namely
	* the first line (a header)
    * the last line (a time stamp)
	* optional lines after `Invalid strips (no letterboxes):`
	
	The syntax of the content line is the following: 
	
`	<line numer>:<space><letterboxes count><space><optional speckle idemtifiers and other comments>`
	
* Extract, if present, the speckle identifiers. 

The character `-` can preceed a number (we call it numerical identifier) or the
letter `l` (we call it line identifier). The numerical identifiers may
occur several times in a line with or without the spaces between them
and be interspersed with some other notes. Here are some examples:

    1: 1 -l
	1: 30 -22-24
    3: 44 -38

* Convert speckle identifiers to their index form.

For numerical identifiers it is
`l <line numer> b <letterbox number>`
For example "1: 30 -22-24" becomes "l 1 b 22" and "l 1 b 24".

The line identifiers are just missing the letterbox part, so "1: 1 -l"
becomes "l 1".

* Convert speckle identifiers to their so called here snippet form.

The form is similar to the index form, but all numbers have 3 digits,
insted of space there is underscore, instead of "l" there is "line"
and instead of "b" there is ""box". So "1: 30 -22-24" becomes
"`line_001 box_22`" and "`line_001 box_24`", and "1: 1 -l" becomes
"`line_001`".

* Extract relevant metadata from the log file.

** The name of the log file has the form `<table-id>-<time
stamp>.log`. Extract the `table-id` as it will be needed later.  **
The first line of the log contains 3 fields, separated by comma, e.g.
`Arguments: input_file=masks/m89.tiff,
djvu_file=Wirzbięta-15_PT11_566.djvu, output_directory=89` Extract the
base name of the "djvu_file", as it will be neede later; let's call it
"table-name".

* Locate the relevant index file.

It in the same subdirectory as the log file and has the name `<table-name>.csv`.
This is the only `csv` file in this directory.

*Actions for Numeric Speckle Identifiers (-<number>): 

For every speckle id found in the log file do the following:

Move the corresponding image file. i.e. the file matching the regular
expression `*<snippet form>*` to the `speckles` directory.
Append the corresponding line from the relevant `.csv` file,
i.e.the regular expression one matching `*<snippet form>*` to
`speckles.csv`.  
		
There should be only one such line in the index and only such file in the directory.
		

Copy the .log file changing the time stamp in its name to the current
one. Add the time stamp line above the existing one.  Change the
content of the new log by placing the all relevant speckle ids in the
brackets.


*Actions for Line Speckle Identifiers (-l):

At first process it as a numerical speckle id, the difference is this
time the regular expressions can fir more then one line or one file.

The next step is to modify the log file. If the log contained also
numerical ids, the new log was already created; if not, create the new
log file following the instruction above.  In the new log put the
whole line speckle identifier in brackers and renumber the remining lines.

Implementation Plan

    Directory Traversal:
        Locate .log files containing -.

    Log Parsing:
        Extract numeric (-<number>) and line (-l) speckle identifiers.
        Determine corresponding image and CSV files.

    File Operations:
        Move speckle image files to the speckles directory.
        Update the .log file and write the new version.
        Append data to speckles.csv.

    Error Handling:
        Handle missing files gracefully with appropriate logging.
