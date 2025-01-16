import os
import sys
import cv2
import numpy as np
from datetime import datetime

# Script version
VERSION = "2.5"

def log_message(log_file, message):
    """Helper function to write messages to the log file."""
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")
    print(message)  # Immediate feedback

def find_path(binary, start_col, log_file):
    """Find a white pixel path from top to bottom starting in the given column."""
    height, width = binary.shape
    path = []

    # Start at the first row in the given column
    x = start_col
    for y in range(height):
        if binary[y, x] == 255:  # Current column has a white pixel
            path.append((y, x))
        elif x > 0 and binary[y, x - 1] == 255:  # Check left neighbor
            x -= 1
            path.append((y, x))
        elif x < width - 1 and binary[y, x + 1] == 255:  # Check right neighbor
            x += 1
            path.append((y, x))
        else:
            log_message(log_file, f"Path terminated at row {y}, column {x}")
            break  # Dead end, stop the path

    log_message(log_file, f"Path found: {path[:10]}... (truncated for brevity)")
    return path

def split_into_glyphs(image, output_dir, file_basename, log_file):
    """Split the image into glyphs using white pixel paths and save them."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    glyph_number = 0
    log_entries = []

    x_start = 0
    processed_columns = set()  # Track processed columns to prevent loops

    while x_start < gray.shape[1]:
        log_message(log_file, f"Starting at column {x_start}")

        # Find the first column with non-white pixels
        while x_start < gray.shape[1] and np.all(gray[:, x_start] == 255):
            x_start += 1

        if x_start >= gray.shape[1]:
            break

        # Prevent infinite loops by ensuring no column is processed twice
        if x_start in processed_columns:
            log_message(log_file, f"Column {x_start} already processed. Skipping.")
            break
        processed_columns.add(x_start)

        # Find the next path
        path = find_path(gray, x_start, log_file)

        if not path:
            log_message(log_file, f"No path found starting at column {x_start}")
            break

        # Determine the cut position from the path
        x_end = max(p[1] for p in path) + 1

        # Extract the glyph image
        glyph_image = gray[:, x_start:x_end]
        padded_glyph = cv2.copyMakeBorder(glyph_image, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=255)

        glyph_number += 1
        glyph_dir = os.path.join(output_dir, os.path.splitext(file_basename)[0] + ".glyph")
        os.makedirs(glyph_dir, exist_ok=True)

        output_path = os.path.join(glyph_dir, f"{glyph_number:02d}_{os.path.splitext(file_basename)[0]}.tiff")
        cv2.imwrite(output_path, padded_glyph)

        log_entries.append(f"Glyph {glyph_number}: Columns [{x_start}:{x_end}]")
        log_message(log_file, f"Glyph {glyph_number}: Columns [{x_start}:{x_end}]")

        x_start = x_end

    return glyph_number, log_entries

def process_directory(input_dir):
    """Main function to process all subdirectories and files."""
    log_file = f"PT_glyphs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_message(log_file, f"Script version: {VERSION}")

    for subdir in sorted(os.listdir(input_dir)):  # Process subdirectories alphabetically
        subdir_path = os.path.join(input_dir, subdir)
        if os.path.isdir(subdir_path):
            print(f"Processing directory: {subdir}")  # Progress report
            log_message(log_file, f"Processing directory: {subdir}")

            for file_name in sorted(os.listdir(subdir_path)):  # Process files alphabetically
                if file_name.lower().endswith('.tiff'):
                    print(f"  Processing file: {file_name}")  # Progress report
                    log_message(log_file, f"Processing file: {file_name}")
                    file_path = os.path.join(subdir_path, file_name)
                    image = cv2.imread(file_path)

                    if image is None:
                        log_message(log_file, f"ERROR: Unable to read file {file_name} in {subdir}")
                        print(f"    ERROR: Unable to read file {file_name}")  # Progress report
                        continue

                    glyphs_output_dir = subdir_path  # Save glyphs in the same *lines directory
                    glyph_count, glyph_logs = split_into_glyphs(image, glyphs_output_dir, file_name, log_file)
                    log_message(log_file, f"{file_name}: {glyph_count} glyphs detected.")
                    print(f"    {glyph_count} glyphs detected.")  # Progress report
                    for glyph_log in glyph_logs:
                        log_message(log_file, glyph_log)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python PT_glyphs.py <input_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)

    process_directory(input_directory)
