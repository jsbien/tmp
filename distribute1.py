# distribute1.py - Version 1.4

import os
import sys
import cv2
import numpy as np
import glob
import matplotlib.pyplot as plt

print("distribute1.py - Version 1.4")


def get_number_from_filename(filename, pattern):
    import re
    match = re.search(pattern, filename)
    if match:
        return int(match.group(1))
    return None


def display_images(image_paths, title):
    images = []
    for img_path in image_paths:
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Unable to read {img_path}")
            continue
        images.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # Convert BGR to RGB for matplotlib

    num_images = len(images)

    if num_images == 0:
        print("No images to display.")
        return

    cols = int(np.ceil(np.sqrt(num_images)))
    rows = int(np.ceil(num_images / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(12, 8))
    fig.suptitle(title)
    plt.tight_layout(pad=2)

    for idx, img in enumerate(images):
        r, c = divmod(idx, cols)
        ax = axes[r, c] if rows > 1 else (axes[c] if cols > 1 else axes)
        ax.imshow(img)
        ax.axis('off')

    plt.show()


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
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
