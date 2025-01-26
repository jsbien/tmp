import cv2
import os
import numpy as np
from datetime import datetime

# Script version
VERSION = "1.1"

def log_message(log_file, message):
    """Helper function to write messages to the log file."""
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")
    print(message)  # Immediate feedback

def process_image(file_path, output_dir, log_file):
    """Process a single image to detect and filter contours."""
    # Read the binary image
    binary = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

    if binary is None:
        log_message(log_file, f"ERROR: Unable to read file {file_path}")
        return

    # Add a white border to prevent edge detection
    binary = cv2.copyMakeBorder(binary, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=255)

    # Find contours and hierarchy
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    log_message(log_file, f"Number of contours found: {len(contours)}")

    # Analyze hierarchy and process top-level contours
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    glyph_count = 0

    for i, contour in enumerate(contours):
        # Check if the contour is a top-level contour (no parent)
        if hierarchy[0, i, 3] == -1:
            x, y, w, h = cv2.boundingRect(contour)

            # Add padding with white pixels
            pad = 2  # Padding size
            x_start = max(0, x - pad)
            y_start = max(0, y - pad)
            x_end = min(binary.shape[1], x + w + pad)
            y_end = min(binary.shape[0], y + h + pad)

            # Extract the glyph with padding
            glyph = binary[y_start:y_end, x_start:x_end]

            # Save the glyph
            glyph_count += 1
            output_file = os.path.join(output_dir, f"{base_name}-{glyph_count}.png")
            cv2.imwrite(output_file, glyph)
            log_message(log_file, f"Saved glyph to {output_file}")

    # Visualize contours
    contour_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)
    debug_path = os.path.join(output_dir, f"{base_name}_contours.png")
    cv2.imwrite(debug_path, contour_image)
    log_message(log_file, f"Saved contour visualization to {debug_path}")

def process_directory(input_dir):
    """Process all binary images in the input directory."""
    log_file = f"contour_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_message(log_file, f"Script version: {VERSION}")
    log_message(log_file, f"Processing input directory: {input_dir}")

    output_dir = os.path.join(input_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    for file_name in sorted(os.listdir(input_dir)):
        if file_name.lower().endswith(('.png', '.jpg', '.tiff')):
            file_path = os.path.join(input_dir, file_name)
            log_message(log_file, f"Processing file: {file_name}")
            process_image(file_path, output_dir, log_file)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python contour_filter.py <input_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)

    process_directory(input_directory)
