The directory DjVu contains the file with the base names in the form:
<printer>-<font>_PT<fascicule>_<plate>

<printer> is an alphabetic string sometimes with non-ASCII letters
<font> starts with a two digit number which can have various postfixes
<fascicule> is a two digit number
<plate> is a tree digit number

Please write a script named `names.py' which will parse the names and
place the results in the CSV file named names.csv, which is present in
the root directory and in the beginning contains only the
header. Additionally please fill the `number' field with the
subsequent numbers starting with 1.

If possible please commit the script to the repository.