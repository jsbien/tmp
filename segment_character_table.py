import sys
import os
from PyQt5.QtGui import QImage, QTransform, QPolygon
from PyQt5.QtCore import QRect, QPoint

def is_black_and_white(image):
    # Convert the image to a format we can easily inspect
    image = image.convertToFormat(QImage.Format_Indexed8)
    
    unique_colors = set()
    
    for y in range(image.height()):
        for x in range(image.width()):
            unique_colors.add(image.pixel(x, y))
            if len(unique_colors) > 2:
                return False
    
    return len(unique_colors) == 2

def detect_black_index(image):
    colortable = image.colorTable()
    if len(colortable) < 2:
        raise ValueError("Color table does not have exactly 2 colors.")
    if colortable[0] > colortable[1]:
        return 1
    return 0

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
            strip_end = i-1
            element_strips.append((strip_start, strip_end))
        strip_start = i
        background_strip = background

    if strip_start < len(sums) and not background_strip:
        strip_end = len(sums) - 1
        element_strips.append((strip_start, strip_end))
    return element_strips

def find_overlap_region(box1, box2):
    overlap_x0 = max(box1.left(), box2.left())
    overlap_y0 = max(box1.top(), box2.top())
    overlap_x1 = min(box1.right(), box2.right())
    overlap_y1 = min(box1.bottom(), box2.bottom())

    if overlap_x0 < overlap_x1 and overlap_y0 < overlap_y1:
        return QRect(overlap_x0, overlap_y0, overlap_x1 - overlap_x0, overlap_y1 - overlap_y0)
    else:
        return None

def split_polygonal(image, box1, box2):
    overlap_region = find_overlap_region(box1, box2)
    if overlap_region:
        diagonal_cut = QPolygon([QPoint(overlap_region.left(), overlap_region.top()),
                                 QPoint(overlap_region.right(), overlap_region.bottom())])
        box1.adjust(0, 0, -diagonal_cut.boundingRect().width(), -diagonal_cut.boundingRect().height())
        box2.adjust(diagonal_cut.boundingRect().width(), diagonal_cut.boundingRect().height(), 0, 0)
    return [box1, box2]

def calculate_letter_boxes_with_splits(image, xstrips):
    boxes = []
    (w, h) = (image.width(), image.height())
    rotate = QTransform()
    rotate.rotate(90)
    for line_num, (y0, y1) in enumerate(xstrips, start=1):
        cur_image = image.copy(0, y0, w, y1-y0).transformed(rotate)
        ystrips = calculate_cutlines_locations(calculate_horizontal_sums(cur_image))
        for i, (x0, x1) in enumerate(ystrips):
            box = QRect(x0, y0, x1-x0, y1-y0)
            if i > 0:
                prev_box = boxes[-1][2]
                if prev_box.intersects(box):
                    boxes[-1][2], box = split_polygonal(image, prev_box, box)
            boxes.append((line_num, i+1, box))
    return boxes

def write_index_file(letter_boxes, input_filename, image_height):
    base_filename = input_filename.replace("_mask", "")
    index_filename = f"{base_filename}.csv"
    with open(index_filename, "w") as index_file:
        for row_num, (line_num, box_num, box) in enumerate(letter_boxes, start=1):
            x = box.left()
            y = image_height - box.bottom()  # Adjust for bottom-left origin
            w = box.width()
            h = box.height()
            index_line = f"{row_num};file:{base_filename}.djvu?djvuopts=&page=1&highlight={x},{y},{w},{h};{base_filename} l {line_num} b {box_num}; ※"
            index_file.write(index_line + "\n")

def write_letter_box_images(image, letter_boxes, input_filename):
    for line_num, box_num, box in letter_boxes:
        image_path = f"{input_filename}_line_{line_num:03}_box_{box_num:03}.png"
        cur_image = image.copy(box)
        cur_image.save(image_path)

def segment_image(image_path):
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"Error: The file '{image_path}' does not exist.")
        return

    # Print the file path for debugging
    print(f"Attempting to open file: {image_path}")

    # Load the image using QImage
    image = QImage(image_path)

    # Check if the image was loaded successfully
    if image.isNull():
        print(f"Error: Failed to load the image from '{image_path}'.")
        return
    else:
        print(f"Image loaded successfully from '{image_path}'.")

    # Print some properties of the loaded image
    print(f"Image size: {image.width()}x{image.height()}")
    print(f"Image depth: {image.depth()} bits per pixel")

    # Ensure it is a black and white image
    if not is_black_and_white(image):
        print("Error: The selected file is not a binary black-and-white image.")
        return

    # Now proceed with the colortable check
    colortable = image.colorTable()
    if len(colortable) != 2:
        print("Error: The image does not have exactly 2 colors in the color table.")
        return

    strips = calculate_horizontal_sums(image)
    hor_lines = calculate_cutlines_locations(strips)
    letter_boxes = calculate_letter_boxes_with_splits(image, hor_lines)
    write_index_file(letter_boxes, image_path, image.height())
    write_letter_box_images(image, letter_boxes, image_path)
    return letter_boxes

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    segment_image(image_path)
