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
    """Process a single image to extract glyphs using closed polynomial chains, preserving the original height."""
#    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

    if image is None:
        log_message(log_file, f"ERROR: Unable to read file {file_path}")
        return

    binary = image  # Use the binary input as-is

    # Find contours
#    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    log_message(log_file, f"{len(contours)} contours found in {file_path}")

    if len(contours) == 0:
        log_message(log_file, "No contours detected. Check the input image.")
        return

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    glyph_count = 0

    for contour in contours:
        # Approximate the contour with a polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)  # Adjust epsilon for smoothness
        polygon = cv2.approxPolyDP(contour, epsilon, True)

        # Create a mask for the polygon
        mask = np.zeros_like(binary)
        cv2.fillPoly(mask, [polygon], 255)  # Fill the polygon area with white

        # Use the mask to preserve the original image height
        cropped_glyph = np.zeros_like(binary)
        cropped_glyph[:, :] = 255  # Start with a blank white image
        cropped_glyph = cv2.bitwise_and(cropped_glyph, binary, mask=mask)

        # Pad the glyph
        padded_glyph = cv2.copyMakeBorder(cropped_glyph, 0, 0, 2, 2, cv2.BORDER_CONSTANT, value=255)

        # Save the glyph
        glyph_count += 1
        output_file = os.path.join(output_dir, f"{base_name}-{glyph_count}.png")
        cv2.imwrite(output_file, padded_glyph)
        log_message(log_file, f"Saved glyph {glyph_count} to {output_file}")

        # Debug: Save the polygon outline for visualization
        debug_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        cv2.polylines(debug_image, [polygon], True, (0, 255, 0), 1)
        debug_path = os.path.join(output_dir, f"{base_name}-{glyph_count}_polygon.png")
        cv2.imwrite(debug_path, debug_image)
        log_message(log_file, f"Polygon outline saved to {debug_path}")

    if glyph_count == 0:
        log_message(log_file, "No glyphs saved. Double-check the contour extraction logic.")


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
        csys.exit(1)

    process_directory(input_directory)
