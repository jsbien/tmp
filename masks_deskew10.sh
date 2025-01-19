for file in *.tiff; do
    convert "$file" -deskew 10% -despeckle  -debug Transform "$fil_Re"
done
