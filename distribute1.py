# distribute1.py - Version 1.3

import os
import sys
import cv2
import numpy as np
import glob

print("distribute1.py - Version 1.3")


def get_number_from_filename(filename, pattern):
    import re
    match = re.search(pattern, filename)
    if match:
        return int(match.group(1))
    return None


def display_images(image_paths, title):
    images = []
    dimensions = []
    for img_path in image_paths:
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Unable to read {img_path}")
            continue
        images.append(img)
        dimensions.append((img.shape[0], img.shape[1]))

    num_images = len(images)

    if num_images == 0:
        print("No images to display.")
        return

    # Calculate the grid dimensions dynamically
    cols = int(np.ceil(np.sqrt(num_images)))
    rows = int(np.ceil(num_images / cols))

    # Calculate max dimensions for each row and column
    max_heights = [0] * rows
    max_widths = [0] * cols

    for idx, (h, w) in enumerate(dimensions):
        r, c = divmod(idx, cols)
        max_heights[r] = max(max_heights[r], h)
        max_widths[c] = max(max_widths[c], w)

    grid_height = sum(max_heights)
    grid_width = sum(max_widths)

    grid = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)

    y_offset = 0
    for r in range(rows):
        x_offset = 0
        for c in range(cols):
            idx = r * cols + c
            if idx >= num_images:
                break
            img = images[idx]
            h, w = img.shape[:2]
            grid[y_offset:y_offset+h, x_offset:x_offset+w] = img
            x_offset += max_widths[c]
        y_offset += max_heights[r]

    cv2.imshow(title, grid)


def main():
    if len(sys.argv) != 2:
        print("Usage: python distribute1.py <dir>")
        sys.exit(1)

    input_dir = sys.argv[1]

    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a directory.")
        sys.exit(1)

    files = glob.glob(os.path.join(input_dir, '*.png'))
    number1_set = sorted(set(get_number_from_filename(f, r'm(\d+)_') for f in files))

    for number1 in number1_set:
        number2_groups = {}
        for file in files:
            num1 = get_number_from_filename(file, r'm(\d+)_')
            num2 = get_number_from_filename(file, r'_lines_(\d+)_')
            if num1 == number1:
                if num2 not in number2_groups:
                    number2_groups[num2] = []
                number2_groups[num2].append(file)

        for number2, image_group in sorted(number2_groups.items()):
            display_images(image_group, f"Number1: {number1}, Number2: {number2}")
            key = cv2.waitKey(0)
            if key == 27:  # Escape key
                confirm = input("Exit (y/n)? ")
                if confirm.lower() == 'y':
                    cv2.destroyAllWindows()
                    sys.exit(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
