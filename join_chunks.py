import sys
import os
import cv2
import numpy as np
import re

# Script version
VERSION = "1.3"

def log(msg):
    print(f"[join_chunks v{VERSION}] {msg}")

def remove_horizontal_padding(img, side='both', pad=2):
    h, w = img.shape[:2]
    if side == 'left':
        return img[:, pad:]
    elif side == 'right':
        return img[:, :w - pad]
    elif side == 'both':
        return img[:, pad:w - pad]
    else:
        raise ValueError("Invalid side argument: use 'left', 'right', or 'both'")

def extract_prefix_and_number(filename):
    match = re.match(r"^(.*)_(\d{2})\.png$", os.path.basename(filename))
    if not match:
        raise ValueError(f"Filename does not match expected pattern '<prefix>_NN.png': {filename}")
    return match.group(1), int(match.group(2))

def build_filename(prefix, number, directory):
    return os.path.join(directory, f"{prefix}_{number:02d}.png")

def join_chunks(file1, file2):
    img1 = cv2.imread(file1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(file2, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        log("Error: One of the input files could not be read.")
        sys.exit(1)

    # Extract numeric suffixes and validate
    prefix1, num1 = extract_prefix_and_number(file1)
    prefix2, num2 = extract_prefix_and_number(file2)

    if prefix1 != prefix2:
        log("Error: File prefixes do not match.")
        sys.exit(1)

    if abs(num1 - num2) != 1:
        log(f"Error: File numbers are not consecutive: {num1}, {num2}")
        sys.exit(1)

    # Ensure correct order
    if num1 > num2:
        file1, file2 = file2, file1
        img1, img2 = img2, img1
        num1, num2 = num2, num1

    # Remove 2 pixels padding from the joining sides
    img1_trimmed = remove_horizontal_padding(img1, side='right', pad=2)
    img2_trimmed = remove_horizontal_padding(img2, side='left', pad=2)

    # Check heights match, else resize
    if img1_trimmed.shape[0] != img2_trimmed.shape[0]:
        log("Warning: Image heights do not match. Resizing second image to match first.")
        img2_trimmed = cv2.resize(img2_trimmed, (img2_trimmed.shape[1], img1_trimmed.shape[0]))

    joined = np.hstack((img1_trimmed, img2_trimmed))

    # Generate output path automatically
    output_name = f"{prefix1}_{num1:02d}+{num2:02d}.png"
    output_path = os.path.join(os.path.dirname(file1), output_name)

    cv2.imwrite(output_path, joined)
    log(f"Joined image saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python join_chunks.py <file1> [file2]")
        sys.exit(1)

    file1 = sys.argv[1]

    if len(sys.argv) == 3:
        file2 = sys.argv[2]
    else:
        # Infer second filename by incrementing number
        prefix, num1 = extract_prefix_and_number(file1)
        num2 = num1 + 1
        directory = os.path.dirname(file1)
        file2 = build_filename(prefix, num2, directory)
        log(f"Inferred second file: {file2}")

    join_chunks(file1, file2)
