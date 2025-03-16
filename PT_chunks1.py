# still no output
import os
import sys
import cv2
import numpy as np
from datetime import datetime

# Script version
VERSION = "4.0"

def log_message(log_file, message):
    """Helper function to write messages to the log file."""
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")
    print(message)  # Immediate feedback

def split_into_chunks(image, output_dir, file_basename, log_file):
    """Split the image into chunks using vertical gaps and save them."""
    # Convert to binary if not already
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    height, width = binary.shape

    # Find vertical gaps
    column_sums = np.sum(binary == 255, axis=0)  # Count white pixels per column
    gap_columns = np.where(column_sums == height)[0]  # Full white columns

    # Split based on gaps
    chunk_start = 0
    chunk_count = 0
    for col in gap_columns:
        if col - chunk_start > 1:  # Ensure non-empty chunk
            chunk = image[:, chunk_start:col]
            output_file = os.path.join(output_dir, f"{file_basename}_chunk_{chunk_count+1}.png")
            cv2.imwrite(output_file, chunk)
            log_message(log_file, f"Saved chunk {chunk_count+1} to {output_file}")
            chunk_count += 1
        chunk_start = col + 1

    # Save the last chunk
    if chunk_start < width:
        chunk = image[:, chunk_start:]
        output_file = os.path.join(output_dir, f"{file_basename}_chunk_{chunk_count+1}.png")
        cv2.imwrite(output_file, chunk)
        log_message(log_file, f"Saved chunk {chunk_count+1} to {output_file}")

def process_image(file_path, output_dir, log_file):
    """Process a single image to extract glyphs and save them with padded bounding boxes."""
    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        log_message(log_file, f"ERROR: Unable to read file {file_path}")
        return

    file_basename = os.path.splitext(os.path.basename(file_path))[0]
    split_into_chunks(image, output_dir, file_basename, log_file)

def process_directory(input_dir):
    """Process all PNG files in the input directory."""
    log_file = f"glyph_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_message(log_file, f"Script version: {VERSION}")
    log_message(log_file, f"Processing input directory: {input_dir}")

    output_dir = os.path.join(input_dir, "glyphs")
    os.makedirs(output_dir, exist_ok=True)

    for file_name in sorted(os.listdir(input_dir)):
        if file_name.lower().endswith('.png'):
            file_path = os.path.join(input_dir, file_name)
            log_message(log_file, f"Processing file: {file_name}")
            process_image(file_path, output_dir, log_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python glyph_extraction.py <input_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)

    process_directory(input_directory)
