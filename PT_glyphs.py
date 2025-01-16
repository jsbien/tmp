import os
import sys
import cv2
import numpy as np
from datetime import datetime

# Script version
VERSION = "3.0"

def log_message(log_file, message):
    """Helper function to write messages to the log file."""
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")
    print(message)  # Immediate feedback

def find_vertical_gaps(binary, log_file):
    """Find vertical gaps composed of columns of white pixels."""
    height, width = binary.shape
    gaps = []

    in_gap = False
    gap_start = 0

    for x in range(width):
        if np.all(binary[:, x] == 255):  # Column is fully white
            if not in_gap:
                gap_start = x
                in_gap = True
        else:
            if in_gap:
                gaps.append((gap_start, x - 1))
                log_message(log_file, f"Gap found: Columns [{gap_start}:{x - 1}]")
                in_gap = False

        # Log column classification for debugging
        if np.all(binary[:, x] == 255):
            log_message(log_file, f"Column {x}: Fully white")
        else:
            log_message(log_file, f"Column {x}: Contains black pixels")

    if in_gap:  # Handle gap ending at the last column
        gaps.append((gap_start, width - 1))
        log_message(log_file, f"Gap found: Columns [{gap_start}:{width - 1}]")

    if not gaps:
        log_message(log_file, "No gaps found. The line might have no fully white columns.")
    return gaps

def split_into_chunks(image, output_dir, file_basename, log_file):
    """Split the image into chunks using vertical gaps and save them."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    gaps = find_vertical_gaps(binary, log_file)

    chunk_number = 0
    prev_gap_end = 0

    for gap_start, gap_end in gaps:
        # Extract the chunk between the previous gap and the current gap
        chunk_image = binary[:, prev_gap_end:gap_start]
        if chunk_image.shape[1] > 0:  # Ignore empty chunks
            padded_chunk = cv2.copyMakeBorder(chunk_image, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=255)

            chunk_number += 1
            chunk_dir = os.path.join(output_dir, os.path.splitext(file_basename)[0] + ".glyph")
            os.makedirs(chunk_dir, exist_ok=True)

            output_path = os.path.join(chunk_dir, f"chunk_{chunk_number:02d}_{os.path.splitext(file_basename)[0]}.tiff")
            cv2.imwrite(output_path, padded_chunk)

            log_message(log_file, f"Chunk {chunk_number}: Columns [{prev_gap_end}:{gap_start}] saved to {output_path}")

        prev_gap_end = gap_end + 1

    # Handle the last chunk after the final gap
    if prev_gap_end < binary.shape[1]:
        chunk_image = binary[:, prev_gap_end:]
        padded_chunk = cv2.copyMakeBorder(chunk_image, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=255)

        chunk_number += 1
        chunk_dir = os.path.join(output_dir, os.path.splitext(file_basename)[0] + ".glyph")
        os.makedirs(chunk_dir, exist_ok=True)

        output_path = os.path.join(chunk_dir, f"chunk_{chunk_number:02d}_{os.path.splitext(file_basename)[0]}.tiff")
        cv2.imwrite(output_path, padded_chunk)

        log_message(log_file, f"Chunk {chunk_number}: Columns [{prev_gap_end}:{binary.shape[1]}] saved to {output_path}")

    return chunk_number

def process_directory(input_dir):
    """Main function to process all subdirectories and files."""
    log_file = f"PT_chunks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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

                    chunks_output_dir = subdir_path  # Save chunks in the same *lines directory
                    chunk_count = split_into_chunks(image, chunks_output_dir, file_name, log_file)
                    log_message(log_file, f"{file_name}: {chunk_count} chunks detected.")
                    print(f"    {chunk_count} chunks detected.")  # Progress report

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python PT_chunks.py <input_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)

    process_directory(input_directory)
