In this phase we run segmentation on all the tables.

The indywidual tables are segmented with `segment_character_table.py',
we need a wraper named 'segment-all.py'.

The wrapper is to loop over lines in names.csv (of course skipping the
header) and extract two fields: the first one called here "id", and
the second one called here "name".

For every line do the following:

1. Create a directory named "id" if it does not exist already.

2. Create the path masks/m<id>.tiff, we will called it "input".

3. Run `segment_character_table.py' with the arguments:
   input
   name
   id

For example, for the line

01,Augezdecki-01_PT08_402.djvu,Augezdecki,01,08,402

run

python3 segment_character_table.py masks/m01.tiff Augezdecki-01_PT08_402.djvu 10

4. On the console print some messages about the progress
