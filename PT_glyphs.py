import os
import sys
import cv2
import numpy as np
from datetime import datetime

# Script version
VERSION = "1.4"

def log_message(log_file, message):
    """Helper function to write messages to the log file."""
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")

def find_cut_path(binary):
    """Find the least-cost path of white pixels from top to bottom."""
    height, width = binary.shape
    cost = np.full((height, width), np.inf)
    path = np.zeros_like(binary, dtype=int)

    # Initialize the first row
    for x in range(width):
        cost[0, x] = 0 if binary[0, x] == 255 else np.inf

    # Dynamic programming to calculate the cost
    for y in range(1, height):
        for x in range(width):
            if binary[y, x] == 255:  # Only consider white pixels
                min_cost = cost[y-1, max(0, x-1):min(width, x+2)].min()
                cost[y, x] = min_cost + 1
                path[y, x] = np.argmin(cost[y-1, max(0, x-1):min(width, x+2)]) + max(0, x-1)

    # Backtrack to find the path
    cut_path = []
    x = np.argmin(cost[-1])
    for y in range(height-1, -1, -1):
        cut_path.append((y, x))
        x = path[y, x]

    return cut_path

def split_into_glyphs(image, output_dir, file_basename):
    """Split the image into glyphs using white pixel paths and save them."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    glyph_number = 0
    log_entries = []

    x_start = 0
    while x_start < binary.shape[1]:
        # Find the next vertical cut path
        cut_path = find_cut_path(binary[:, x_start:])
        if not cut_path:
            break

        # Use the cut path to split the glyph
        x_end = x_start + max(p[1] for p in cut_path)
        glyph_image = binary[:, x_start:x_end]
        padded_glyph = cv2.copyMakeBorder(glyph_image, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=0)

        glyph_number += 1
        glyph_dir = os.path.join(output_dir, os.path.splitext(file_basename)[0] + "_glyphs")
        os.makedirs(glyph_dir, exist_ok=True)

        output_path = os.path.join(glyph_dir, f"{glyph_number:02d}_{os.path.splitext(file_basename)[0]}.tiff")
        cv2.imwrite(output_path, padded_glyph)

        log_entries.append(f"Glyph {glyph_number}: Columns [{x_start}:{x_end}]")
        x_start = x_end

    return glyph_number, log_entries

def process_directory(input_dir):
    """Main function to process all subdirectories and files."""
    log_file = f"PT_glyphs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_message(log_file, f"Script version: {VERSION}")

    for subdir in os.listdir(input_dir):
        subdir_path = os.path.join(input_dir, subdir)
        if os.path.isdir(subdir_path):
            print(f"Processing directory: {subdir}")  # Progress report
            glyphs_dir = f"{subdir_path}_glyphs"
            os.makedirs(glyphs_dir, exist_ok=True)

            for file_name in os.listdir(subdir_path):
                if file_name.lower().endswith('.tiff'):
                    print(f"  Processing file: {file_name}")  # Progress report
                    file_path = os.path.join(subdir_path, file_name)
                    image = cv2.imread(file_path)

                    if image is None:
                        log_message(log_file, f"ERROR: Unable to read file {file_name} in {subdir}")
                        print(f"    ERROR: Unable to read file {file_name}")  # Progress report
                        continue

                    glyph_count, glyph_logs = split_into_glyphs(image, glyphs_dir, file_name)
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
