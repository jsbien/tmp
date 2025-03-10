The script glyphs2meta.py take 4 arguments: input directory, output
directory, so called dsed directory and so called meta file.

The goal
--------

The input directory contains PNG files. The goal is to create for
every PNG file a sidecar file in the output directory. The sidecar
files are single ron CVS file with a header, the base name is
identical as the PNG file and the extension is csv.

The header is:
table, row, glyph, id, printer, font, fascicule, year, plate, description

The base name of the PNG files has the form

t<number1>_l<number2>g<number3>

<number3> is copied to the sidecar file to the column 3 (glyph).

<number2> is copied to the sidecar file to the column 2 (row).

<number1> is copied to the sidecar file to the column 1 (table).

Moreover <number1> is used to locate the appropriate row in the meta
file, which is a CVS file with the header:

number,filename,printer,font,fascicule,plate

<number1> has to be identical with <number>.


<number2>, <number3>, <printer> and <font> are used to create the
identifier which is written to the sidecar file in column 4 (id). A
Python code is already available for creating the identifier.

<printer>, <font>, <fascicule> and <plate> are written respectively as
columns 5-6 and 9 of the sidecar file.

The <filename> is modified by suffixing the base name by "_4dsed" and
changing the extension to "txt".

The file with this name is looked up in the dsed directory. It is in
the format of DjVuLibre djvused program, the relevant fields are Year
and Note. Year is copied to the column 8 (year), and Note to the
column 10 (description) of the sidecar file.

An example
----------

The input file: 

t01_l01g01.png

The row of the meta file:

01,Augezdecki-01_PT08_402.djvu,Augezdecki,01,08,402

The id:

Au-01_0101

The relevant dsed file name:

Augezdecki-01_PT08_402_4dsed.txt

The relevant fields of the file:

Year "1972"
Note "1. Pisma tekstowe, szwabacha M⁸¹. Stopień 20 ww. = 102—103 mm (tercja). — Tabl. 402—404. [402]"

The sidecar file name:

t01_l01g01.csv

Its content:

table, row, glyph, id, printer, font, fascicule, year, plate, description
01,01,01,Au-01_0101,Augezdecki,01,08,1972,402,"1. Pisma tekstowe, szwabacha M⁸¹. Stopień 20 ww. = 102—103 mm (tercja). — Tabl. 402—404. [402]"

Coding
------

The script glyphidx2tex.py contains already the code for parsing the
input file, accessing the meta file and creating the identifier.
