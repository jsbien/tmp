import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

SCRIPT_VERSION = "3.0"

# Color and log mapping for each key
KEY_ACTIONS = {
    Qt.Key_Space: ("green", "glyph", "is glyph"),
    Qt.Key_S: ("blue", "split", "to split"),
    Qt.Key_J: ("orange", "join", "to join"),
    Qt.Key_Delete: ("red", "noise", "is noise")
}

class ImageGrid(QWidget):
    def __init__(self, image_dir):
        super().__init__()
        self.setWindowTitle(f"Image Grid - {os.path.abspath(image_dir)}")
        self.setFocusPolicy(Qt.StrongFocus)

        # Initialize navigation variables
        self.current_index = 0
        self.image_class = {}  # Store the class for each image

        # Get PNG files sorted alphabetically
        self.images = sorted([f for f in os.listdir(image_dir) if f.lower().endswith('.png')])
        self.image_dir = image_dir

        # Create subdirectories if not exist
        for _, subdir, _ in KEY_ACTIONS.values():
            os.makedirs(os.path.join(image_dir, subdir), exist_ok=True)

        # Create a scrollable area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Main widget to hold the grid layout
        content_widget = QWidget()
        self.grid_layout = QGridLayout(content_widget)

        # Display images in the grid
        self.labels = []
        self.max_col = int(len(self.images) ** 0.5) + 1
        for index, image in enumerate(self.images):
            row = index // self.max_col
            col = index % self.max_col
            label = QLabel(self)
            pixmap = QPixmap(os.path.join(image_dir, image))
            label.setPixmap(pixmap)
            label.setStyleSheet("border: 2px solid transparent;")
            self.grid_layout.addWidget(label, row, col)
            self.labels.append(label)

        # Set initial selection
        self.update_selection(0)

        # Set the layout to the content widget and add to scroll area
        content_widget.setLayout(self.grid_layout)
        scroll_area.setWidget(content_widget)

        # Main layout to include scroll area
        main_layout = QGridLayout(self)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # Set focus after initialization
        self.setFocus()

    def update_selection(self, new_index):
        """Update the selection highlighting."""
        # Clear previous selection
        if 0 <= self.current_index < len(self.labels):
            label = self.labels[self.current_index]
            color = self.image_class.get(self.current_index, "transparent")
            label.setStyleSheet(f"border: 2px solid {color};")

        # Update current index
        self.current_index = new_index

        # Highlight the new selection
        if 0 <= self.current_index < len(self.labels):
            self.labels[self.current_index].setStyleSheet("border: 2px solid black;")

    def classify_image(self, key):
        """Classify the currently selected image based on the key press."""
        if key in KEY_ACTIONS:
            color, category, log_message = KEY_ACTIONS[key]
            filename = self.images[self.current_index]

            # Update classification and log
            self.image_class[self.current_index] = color
            print(f"{filename} {log_message}")

            # Update the current label's style
            self.labels[self.current_index].setStyleSheet(f"border: 2px solid {color};")

            # Move to the next image automatically
            next_index = min(self.current_index + 1, len(self.labels) - 1)
            self.update_selection(next_index)

    def move_images(self):
        """Move images to respective directories based on classification."""
        for index, color in self.image_class.items():
            filename = self.images[index]
            _, subdir, _ = next((v for k, v in KEY_ACTIONS.items() if v[0] == color), (None, None, None))
            if subdir:
                source = os.path.join(self.image_dir, filename)
                destination = os.path.join(self.image_dir, subdir, filename)
                shutil.move(source, destination)
                print(f"Moved: {filename} -> {subdir}")

    def keyPressEvent(self, event):
        """Handle keyboard input."""
        key = event.key()

        if key in KEY_ACTIONS:
            # Classify the current image
            self.classify_image(key)
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            # Move images to respective subdirectories and exit
            self.move_images()
            print("Image classification completed.")
            QApplication.quit()
        else:
            # Ignore other keys
            return

    def mousePressEvent(self, event):
        """Ensure the widget gains focus when clicked."""
        self.setFocus()

def main():
    print(f"Script version: {SCRIPT_VERSION}")

    if len(sys.argv) != 2:
        print("Usage: python PT_show.py <image_directory>")
        sys.exit(1)

    image_dir = sys.argv[1]
    if not os.path.isdir(image_dir):
        print(f"Error: {image_dir} is not a valid directory.")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = ImageGrid(image_dir)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
