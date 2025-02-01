# https://chatgpt.com/c/67876b18-42a4-800d-a329-dd2bc7f6e2ac
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

def process_image(file_path, output_dir, log_file):
    """Process a single image to extract glyphs and save them with padded bounding boxes."""
    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        log_message(log_file, f"ERROR: Unable to read file {file_path}")
        return

    binary = image  # Correctly assign binary to the loaded image

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    log_message(log_file, f"{len(contours)} contours found in {file_path}")

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    glyph_count = 0

    for contour in contours:
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        glyph = binary[y:y+h, x:x+w]

        # Pad the glyph to make it a rectangular bounding box
        padded_glyph = cv2.copyMakeBorder(glyph, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=255)

        # Save the glyph
        glyph_count += 1
        output_file = os.path.join(output_dir, f"{base_name}-{glyph_count}.png")
        cv2.imwrite(output_file, padded_glyph)  # No need to invert back since input is already correct
        log_message(log_file, f"Saved glyph {glyph_count} to {output_file}")

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
