for file in *.png; do
    convert "$file" -deskew 10% -despeckle  -debug Transform "$fil_Re"
done
