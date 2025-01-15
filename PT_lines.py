import os
import sys
import cv2
import numpy as np
from datetime import datetime

# Script version
VERSION = "1.0"

def log_message(log_file, message):
    """Helper function to write messages to the log file."""
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")

def is_dewarping_needed(image):
    """Determine if the image needs dewarping based on the straightness of lines."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    return lines is not None

def split_into_lines(image, output_dir):
    """Split the image into lines and save them to the output directory."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by their vertical position (y-coordinate)
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    line_number = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h > 10:  # Ignore very small lines
            line_number += 1
            line_image = image[y:y+h, x:x+w]
            output_path = os.path.join(output_dir, f"{line_number:02d}_{os.path.basename(output_dir)}.tiff")
            cv2.imwrite(output_path, line_image)

    return line_number

def process_directory(input_dir):
    """Main function to process all TIFF files in the input directory."""
    log_file = f"PT_lines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_message(log_file, f"Script version: {VERSION}")

    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith('.tiff'):
            file_path = os.path.join(input_dir, file_name)
            image = cv2.imread(file_path)

            if image is None:
                log_message(log_file, f"ERROR: Unable to read file {file_name}")
                continue

            if not is_dewarping_needed(image):
                log_message(log_file, f"{file_name}: Dewarping not needed.")
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
