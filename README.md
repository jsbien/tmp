The purposes of the segment_character_table.py is to split a graphical
character table into the images of the individual glyphs and to
provide an index to the table in the djview4poliqarp format.

The letterbox coordinates are in the format used by the djview4
program, cf. e.g.  https://github.com/barak/djview4.

Here are the relevant excerpts from the man page (https://djvu.sourceforge.net/doc/man/djview4.html)

START QUOTE

    A local DjVu document URL of the form: 
    file:///path/name.djvu[?djvuopts&keyword=value&...] 

The square brackets delimit the optional components of the
URL.

-highlight=x,y,w,h[,color]

Display a highlighted rectangle at the specified coordinates in the
current page and with the specified color. Coordinates x, y, w, and h
are measured in document image coordinates (not screen
coordinates). The origin is set at the bottom left corner of the
image. The color color must be given in hexadecimal RRGGBB or #RRGGBB
format. 

END QUOTE

'w' and 'h' stand of course for width and height.

We don't use colors and skip the path, so for the coordinates 49,66,157,223
we get

Hochfeder-02_PT01_020bis.djvu?djvuopts=&page=1&highlight=49,66,180,174

The file is the input file name with the postfix '_mask' removed and
the extension changed to 'djvu'.

Moreover  all the relevant data are to be consolidated into an index
supported by 'djview4poliqarp' program
(https://github.com/jsbien/djview-poliqarp_fork). For the time being
the best description of the index format can be found in the my paper
"Towards an inventory of old print characters: Ungler’s Rubricella, a
case study" (http://dx.doi.org/10.47397/tb/44-3/tb138bien-rubricella).

Here are the relevant fragments:

START QUOTE

From the technical point of view the indexes
are just simple CSV files (using semicolon as the
separator). Every line of an index file consists of
three or four fields:

1. The text used for sorting and incremental search.

2. The reference to the relevant image fragment in
the form used by the djview4 viewer mentioned
earlier, namely a Universal Resource Locator.
[...]

3. A description: text displayed for the current
entry in a small window under the index.

4. An optional comment displayed after the entry;
we precede it by ※ (U+203B reference mark)
for a more distinctive display.

END QUOTE

In our case we decide that the first element will be the the running
number of the index line, the third element will the letterbox
location, i.e. table file name without the extension, table line
number and the letterbox number in the line, and the fourth just a
single space and ※.

Hence instead of the present output

Line Number,Box Number,x0,y0,x1,y1
we need

<index line number>;file:Hochfeder-02_PT01_020bis_mask.djvu?djvuopts=&page=1&highlight=<x>,<y>,<w>,<h>;Hochfeder-02_PT01_020bis_mask l 1 b 1; ※

The orMake sure the origin of the coordinates is at the bottom left
corner of the image!

The name of the index should the document base name with the extension
csv, e.g. Hochfeder-02_PT01_020bisOCR.csv.

The header is not needed,

The task of the wrapper 'segment-all.py' is to do for all png
files in the given directory the following operations:

1. For every file <name>_mask.png create subdirectory name just <name>.

2. Run the script segment_character_table.py on every file and move
the created letterbox images to appropriate directories.

3. At the very end concatenate all the *.csv indexes into one index
named all_tables.csv

