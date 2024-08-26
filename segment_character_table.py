# The code extracted from glyphtracer by Jussi Pakkanen
# (https://github.com/jpakkane/glyphtracer) and modified by ChatGPT 3.5
# according to the specification provided by Janusz S. Bień

# Intended to be used for the masks in the PBM format of DjVu document,
# primarily the character tables from "Polonia Typographica"
# (https://github.com/jsbien/early_fonts_inventory)

# TO DO: investigate the warnings produced by Thonny
# TO DO: output the letter box coordinates in the djview4poliqarp format

import sys
from PyQt5.QtGui import QImage, QTransform, QPixmap, QPolygon
from PyQt5.QtCore import QRect, QPoint
from datetime import datetime


def detect_black_index(image):
    colortable = image.colorTable()
    assert(len(colortable) == 2)
    if(colortable[0] > colortable[1]):
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

        # We crossed a region.
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
        # Adjust the boxes based on the diagonal cut
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
            if i > 0:  # Check with previous box for overlap
                prev_box = boxes[-1][2]
                if prev_box.intersects(box):
                    boxes[-1][2], box = split_polygonal(image, prev_box, box)
            print(f"Box {len(boxes)+1}: ({x0}, {y0}), ({x1}, {y1})")  # Debugging print
            boxes.append((line_num, i+1, box))
    return boxes

def write_letter_box_images(image, letter_boxes, input_filename):
    for line_num, box_num, box in letter_boxes:
        image_path = f"{input_filename}_line_{line_num:03}_box_{box_num:03}.png"
        cur_image = image.copy(box)
        cur_image.save(image_path)

def segment_image(image_path):
    input_filename = image_path.split('.')[0]
    image = QImage(image_path)
    if image.isNull() or image.depth() != 1:
        print("Error: Selected file is not a 1 bit image.")
        return

    strips = calculate_horizontal_sums(image)
    hor_lines = calculate_cutlines_locations(strips)
    letter_boxes = calculate_letter_boxes_with_splits(image, hor_lines)
    write_letter_box_images(image, letter_boxes, input_filename)
    return letter_boxes

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    letter_boxes = segment_image(image_path)
    if letter_boxes:
        print("Segmentation completed. Letter box coordinates printed for debugging.")
