import os
import sys
import cv2
import numpy as np
from datetime import datetime

# Script version
VERSION = "1.5"

def log_message(log_file, message):
    """Helper function to write messages to the log file."""
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")

def find_cut_path(binary, log_file=None):
    """Find the least-cost path of white pixels from top to bottom with logging."""
    height, width = binary.shape

    # Precompute pixel costs (0 for black, 1 for white)
    pixel_costs = np.where(binary == 255, 1, np.inf)

    # Initialize cost matrix
    cost = np.full((height, width), np.inf)
    path = np.zeros((height, width), dtype=int)

    # Set up the first row
    cost[0, :] = pixel_costs[0, :]

    if log_file:
        log_message(log_file, f"Image dimensions: {height}x{width}")
        log_message(log_file, "Starting cost computation...")

    # Dynamic programming for cost calculation
    for y in range(1, height):
        for x in range(width):
            if pixel_costs[y, x] == 1:  # Only process white pixels
                left = cost[y - 1, x - 1] if x > 0 else np.inf
                center = cost[y - 1, x]
                right = cost[y - 1, x + 1] if x < width - 1 else np.inf

                # Compute minimum cost and store it
                min_cost = min(left, center, right)
                cost[y, x] = min_cost + 1
                path[y, x] = np.argmin([left, center, right]) - 1 + x if x > 0 else x

        if log_file and y % 100 == 0:
            log_message(log_file, f"Processed row {y}/{height}")

    # Backtrack to find the path
    cut_path = []
    x = np.argmin(cost[-1, :])
    for y in range(height - 1, -1, -1):
        cut_path.append((y, x))
        x = path[y, x]

    if log_file:
        log_message(log_file, "Finished cost computation.")

    return cut_path

def split_into_glyphs(image, output_dir, file_basename, log_file):
    """Split the image into glyphs using white pixel paths and save them."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    glyph_number = 0
    log_entries = []

    x_start = 0
    while x_start < binary.shape[1]:
        # Find the next vertical cut path
        cut_path = find_cut_path(binary[:, x_start:], log_file)
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
        log_message(log_file, f"Glyph {glyph_number}: Columns [{x_start}:{x_end}]")
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
            log_message(log_file, f"Processing directory: {subdir}")
            glyphs_dir = f"{subdir_path}_glyphs"
            os.makedirs(glyphs_dir, exist_ok=True)

            for file_name in os.listdir(subdir_path):
                if file_name.lower().endswith('.tiff'):
                    print(f"  Processing file: {file_name}")  # Progress report
                    log_message(log_file, f"Processing file: {file_name}")
                    file_path = os.path.join(subdir_path, file_name)
                    image = cv2.imread(file_path)

                    if image is None:
                        log_message(log_file, f"ERROR: Unable to read file {file_name} in {subdir}")
                        print(f"    ERROR: Unable to read file {file_name}")  # Progress report
                        continue

                    glyph_count, glyph_logs = split_into_glyphs(image, glyphs_dir, file_name, log_file)
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
