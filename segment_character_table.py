# ChatGPG 24-11-30 https://chatgpt.com/g/g-3s6SJ5V7S-askthecode-git-companion/c/6749c73d-b308-800d-9771-49ee6ce13b16
import sys
import os
from datetime import datetime
from PyQt5.QtGui import QImage, QTransform
from PyQt5.QtCore import QRect


def calculate_horizontal_sums(image):
    (w, h) = (image.width(), image.height())
    black_index = detect_black_index(image)
    sums = []
    for j in range(h):
        total = 0
        for i in range(w):
            if image.pixelIndex(i, j) == black_index:
                total += 1
        sums.append(total)
    return sums


def calculate_cutlines_locations(sums):
    element_strips = []
    cutoff = 0

    if len(sums) == 0:
        return []
    if sums[0] <= cutoff:
        background_strip = True
    else:
        background_strip = False
    strip_start = 0

    for i in range(len(sums)):
        if sums[i] <= cutoff:
            background = True
        else:
            background = False
        if background == background_strip:
            continue

        if background:
            strip_end = i - 1
            element_strips.append((strip_start, strip_end))
        strip_start = i
        background_strip = background

    if strip_start < len(sums) and not background_strip:
        strip_end = len(sums) - 1
        element_strips.append((strip_start, strip_end))
    return [strip for strip in element_strips if strip[1] - strip[0] > 1]  # Filter short strips


def detect_black_index(image):
    colortable = image.colorTable()
    if len(colortable) < 2:
        raise ValueError("Color table does not have exactly 2 colors.")
    if colortable[0] > colortable[1]:
        return 1
    return 0


def calculate_letter_boxes_with_splits(image, xstrips):
    boxes = []
    (w, h) = (image.width(), image.height())
    rotate = QTransform()
    rotate.rotate(90)
    line_counter = 1  # Continuous line numbering starts at 1
    invalid_strips = []  # Collect invalid strips for logging

    for (y0, y1) in xstrips:
        cur_image = image.copy(0, y0, w, y1 - y0).transformed(rotate)
        ystrips = calculate_cutlines_locations(calculate_horizontal_sums(cur_image))
        if ystrips:  # If letterboxes are found
            for i, (x0, x1) in enumerate(ystrips):
                box = QRect(x0, y0, x1 - x0, y1 - y0)
                boxes.append((line_counter, i + 1, box))
            line_counter += 1  # Increment for every valid strip
        else:  # If no letterboxes are found
            invalid_strips.append((y0, y1))  # Collect the coordinates of the invalid strip
    return boxes, invalid_strips


def create_log_filename(base_name, output_directory):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    log_file_name = f"{base_name}-{timestamp}.log"
    return os.path.join(output_directory, log_file_name)


def write_log_file(letter_boxes, input_filename, djvu_file, output_directory, invalid_strips):
    log_file_name = create_log_filename(os.path.splitext(os.path.basename(input_filename))[0], output_directory)
    line_counts = {}
    for line_num, box_num, _ in letter_boxes:
        if line_num not in line_counts:
            line_counts[line_num] = 0
        line_counts[line_num] += 1

    log_content = []
    log_content.append(f"Arguments: input_file={input_filename}, djvu_file={djvu_file}, output_directory={output_directory}")
    for line_num, count in sorted(line_counts.items()):
        log_content.append(f"{line_num}: {count}")
    log_content.append("\nInvalid strips (no letterboxes):")
    for y0, y1 in invalid_strips:
        log_content.append(f"y-coordinates: {y0}-{y1}")
    log_content.append(f"Timestamp: {datetime.now().isoformat()}")

    with open(log_file_name, "w") as log_file:
        log_file.write("\n".join(log_content))
    print(f"Log saved to {log_file_name}")


def write_index_file(letter_boxes, input_filename, djvu_file, output_directory, image_height):
    base_filename = os.path.basename(input_filename).replace("_mask", "")
    table_identifier = os.path.basename(input_filename).lstrip("m").split(".")[0].zfill(3)
    djvu_base_name = os.path.basename(djvu_file).replace(".djvu", "")
    index_filename = os.path.join(output_directory, f"{os.path.basename(djvu_file).replace('.djvu', '.csv')}")

    with open(index_filename, "w") as index_file:
        for row_num, (line_num, box_num, box) in enumerate(letter_boxes, start=1):
            x = box.left()
            y = image_height - box.bottom()
            w = box.width()
            h = box.height()
            entry = f"{table_identifier} l {line_num} b {box_num}"
            description = f"{djvu_base_name} l {line_num} b {box_num}"
            comment = " ※"
            index_line = f"{entry};file:{djvu_file}?djvuopts=&page=1&highlight={x},{y},{w},{h};{description};{comment}"
            index_file.write(index_line + "\n")
    print(f"Index saved to {index_filename}")


def write_letter_box_images(image, letter_boxes, input_filename, output_directory):
    for line_num, box_num, box in letter_boxes:
        image_path = os.path.join(output_directory, f"{os.path.basename(input_filename)}_line_{line_num:03}_box_{box_num:03}.png")
        cur_image = image.copy(box)
        cur_image.save(image_path)


def segment_image(image_path, djvu_file, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    image = QImage(image_path)
    strips = calculate_horizontal_sums(image)
    hor_lines = calculate_cutlines_locations(strips)
    letter_boxes, invalid_strips = calculate_letter_boxes_with_splits(image, hor_lines)

    write_index_file(letter_boxes, image_path, djvu_file, output_directory, image.height())
    write_letter_box_images(image, letter_boxes, image_path, output_directory)
    write_log_file(letter_boxes, image_path, djvu_file, output_directory, invalid_strips)
    return letter_boxes


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <image_path> <djvu_file> [output_directory]")
        sys.exit(1)

    image_path = sys.argv[1]
    djvu_file = sys.argv[2]
    output_directory = sys.argv[3] if len(sys.argv) > 3 else "tmp"

    segment_image(image_path, djvu_file, output_directory)
