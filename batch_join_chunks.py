import os
import re
import cv2
import numpy as np
from collections import defaultdict

# Script version
VERSION = "1.1"

def log(msg):
    print(f"[batch_join_chunks v{VERSION}] {msg}")

def extract_prefix_and_number(filename):
    match = re.match(r"^(.*)_(\d{2})\.png$", filename)
    if not match:
        return None, None
    return match.group(1), int(match.group(2))

def find_consecutive_groups(files):
    grouped = defaultdict(list)
    for f in files:
        prefix, number = extract_prefix_and_number(f)
        if prefix is not None:
            grouped[prefix].append((number, f))

    sequences = []
    for prefix, numbered_files in grouped.items():
        numbered_files.sort()
        group = []
        prev = None
        for num, fname in numbered_files:
            if prev is None or num == prev + 1:
                group.append(fname)
            else:
                if len(group) > 1:
                    sequences.append((prefix, group))
                group = [fname]
            prev = num
        if len(group) > 1:
            sequences.append((prefix, group))
    return sequences

def remove_horizontal_padding(img, side='both', pad=2):
    h, w = img.shape[:2]
    if side == 'left':
        return img[:, pad:]
    elif side == 'right':
        return img[:, :w - pad]
    elif side == 'both':
        return img[:, pad:w - pad]
    else:
        raise ValueError("Invalid side argument")

def join_sequence(filepaths, output_path, dry_run=False):
    if dry_run:
        log(f"[dry-run] Would join {len(filepaths)} files into {output_path}")
        return

    imgs = []
    for i, fp in enumerate(filepaths):
        img = cv2.imread(fp, cv2.IMREAD_GRAYSCALE)
        if img is None:
            log(f"Failed to read {fp}")
            return
        if i == 0:
            img = remove_horizontal_padding(img, side='right')
        elif i == len(filepaths) - 1:
            img = remove_horizontal_padding(img, side='left')
        else:
            img = remove_horizontal_padding(img, side='both')
        imgs.append(img)

    # Match heights if needed
    min_height = min(img.shape[0] for img in imgs)
    imgs_resized = [cv2.resize(im, (im.shape[1], min_height)) for im in imgs]

    joined = np.hstack(imgs_resized)
    cv2.imwrite(output_path, joined)
    log(f"Saved joined file: {output_path}")

def process_directory(directory, dry_run=False):
    files = sorted(f for f in os.listdir(directory) if f.lower().endswith(".png"))
    sequences = find_consecutive_groups(files)
    if not sequences:
        log("No consecutive sequences found.")
        return

    for prefix, group in sequences:
        first_num = extract_prefix_and_number(group[0])[1]
        last_num = extract_prefix_and_number(group[-1])[1]
        output_name = f"{prefix}_{first_num:02d}+{last_num:02d}.png"
        output_path = os.path.join(directory, output_name)
        join_sequence([os.path.join(directory, f) for f in group], output_path, dry_run=dry_run)

if __name__ == "__main__":
    import sys
    if len(sys.argv) not in [2, 3]:
        print("Usage: python batch_join_chunks.py <directory> [--dry-run]")
        sys.exit(1)

    input_dir = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory.")
        sys.exit(1)

    process_directory(input_dir, dry_run=dry_run)
