import os
import cv2
import numpy as np
import logging
from datetime import datetime

# Configure logging
LOG_FILE = "PT_dewarp.log"
# logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')
logging.basicConfig(filename=LOG_FILE, filemode='w', level=logging.INFO, format='%(asctime)s - %(message)s')


def is_text_straight(image):
    """Determine if the lines of text in the image are straight."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Perform Hough Line Transformation
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is None:
        return True  # No lines detected, assume no dewarping needed

    # Check angles of detected lines
    for line in lines:
        rho, theta = line[0]
        angle = np.degrees(theta)
        if not (85 <= angle <= 95 or -5 <= angle <= 5):  # Acceptable range for "straight" lines
            return False

    return True


def dewarp_image(image):
    """Apply dewarping to the image."""
    # Example implementation (this can be adjusted based on specific requirements)
    # Detect contours for perspective transformation
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding box and apply warp
        rect = cv2.minAreaRect(largest_contour)
        box = cv2.boxPoints(rect)
        box = np.array(box, dtype=int)

        # Define points for perspective transformation
        width = max(int(rect[1][0]), int(rect[1][1]))
        height = min(int(rect[1][0]), int(rect[1][1]))
        dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype='float32')
        M = cv2.getPerspectiveTransform(np.array(box, dtype='float32'), dst)
        warped = cv2.warpPerspective(image, M, (width, height))
        return warped
    
    return image  # Return the original if no contours found


def process_directory(input_dir):
    """Process all TIFF files in the specified directory."""
    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(".tiff"):
            input_path = os.path.join(input_dir, file_name)

            try:
                # Read the image
                image = cv2.imread(input_path)

                if image is None:
                    raise ValueError("Unable to read the image.")

                # Check if dewarping is needed
                if is_text_straight(image):
                    status = "w"
                    output_image = image
                else:
                    status = "W"
                    output_image = dewarp_image(image)

                # Save the output
                base_name, _ = os.path.splitext(file_name)
                output_name = f"{base_name}_{status}.png"
                output_path = os.path.join(input_dir, output_name)
                cv2.imwrite(output_path, output_image)

                # Log the result
                logging.info(f"Processed: {file_name}, Status: {status}")

            except Exception as e:
                logging.error(f"Error processing {file_name}: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python PT_dewarp.py <input_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)

    process_directory(input_directory)
    print(f"Processing complete. Log file saved as {LOG_FILE}.")
