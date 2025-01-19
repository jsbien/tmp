import os
import sys
import cv2
import numpy as np
from datetime import datetime

# Script version
VERSION = "1.2"

def log_message(log_file, message):
    """Helper function to write messages to the log file."""
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")

def split_into_lines(image, output_dir):
    """Split the image into horizontal lines and save them to the output directory."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Sum along columns to find horizontal projections
    horizontal_projection = np.sum(binary, axis=1)

    # Detect line positions based on projection
    line_positions = []
    in_line = False
    for i, value in enumerate(horizontal_projection):
        if value > 0 and not in_line:
            in_line = True
            start = i
        elif value == 0 and in_line:
            in_line = False
            end = i
            # Ignore lines shorter than 10 pixels
            if (end - start) >= 10:
                line_positions.append((start, end))

    line_number = 0
    for start, end in line_positions:
        line_number += 1
        line_image = image[start:end, :]
#        output_path = os.path.join(output_dir, f"{line_number:02d}_{os.path.basename(output_dir)}.png")
        output_path = os.path.join(output_dir, f"{os.path.basename(output_dir)}_{line_number:02d}.png")
        cv2.imwrite(output_path, line_image)

    return len(line_positions)

def process_directory(input_dir):
    """Main function to process all TIFF files in the input directory."""
    log_file = f"PT_lines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_message(log_file, f"Script version: {VERSION}")

    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith('.png'):
            file_path = os.path.join(input_dir, file_name)
            image = cv2.imread(file_path)

            if image is None:
                log_message(log_file, f"ERROR: Unable to read file {file_name}")
                continue

            output_dir = os.path.join(input_dir, f"{os.path.splitext(file_name)[0]}_lines")
            os.makedirs(output_dir, exist_ok=True)

            line_count = split_into_lines(image, output_dir)
            log_message(log_file, f"{file_name}: {line_count} lines detected and saved.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python PT_lines.py <input_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)

    process_directory(input_directory)
