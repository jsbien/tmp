import os
import csv
import subprocess
from PyQt5.QtGui import QImage
from segment_character_table import is_black_and_white, detect_black_index

# Paths
CSV_FILE = "names.csv"
DJVU_DIR = "DjVu"
MASKS_DIR = "masks"

# Ensure the output directory exists
os.makedirs(MASKS_DIR, exist_ok=True)

def process_djvu_files():
    # Read names.csv
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        return
    
    with open(CSV_FILE, mode="r", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)  # Skip the header
        
        for row in reader:
            try:
                number, filename = row[0], row[1]
                djvu_file = os.path.join(DJVU_DIR, filename)
                output_file = os.path.join(MASKS_DIR, f"m{number}.tiff")
                
                # Check if the DjVu file exists
                if not os.path.exists(djvu_file):
                    print(f"Warning: {djvu_file} does not exist. Skipping.")
                    continue
                
                # Run ddjvu to extract the mask
                try:
                    subprocess.run(
                        ["ddjvu", "-mode=mask", "-format=tiff", djvu_file, output_file],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                except subprocess.CalledProcessError as e:
                    print(f"Error processing {djvu_file}: {e.stderr.decode().strip()}")
                    continue
                
                # Validate the output is binary
                if not os.path.exists(output_file):
                    print(f"Error: Output file {output_file} not created.")
                    continue
                
                # Load the output file into a QImage
                image = QImage(output_file)
                if image.isNull():
                    print(f"Warning: Could not load {output_file} as an image.")
                    continue
                
                if not is_black_and_white(image) and not detect_black_index(image):
                    print(f"Warning: Output file {output_file} is not binary.")
                
                print(f"Successfully processed {djvu_file} -> {output_file}")
            
            except IndexError:
                print(f"Error: Malformed row in CSV: {row}")
                continue

if __name__ == "__main__":
    process_djvu_files()
