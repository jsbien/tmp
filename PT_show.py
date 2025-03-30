import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QScrollArea, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import re
from itertools import groupby

SCRIPT_VERSION = "4.9"

# Color and log mapping for each key
KEY_ACTIONS = {
    Qt.Key_Space: ("green", "glyph", "is glyph"),
    Qt.Key_S: ("blue", "split", "to split"),
    Qt.Key_J: ("orange", "join", "to join"),
    Qt.Key_N: ("red", "noise", "is noise")
}

class ImageGrid(QWidget):
    def __init__(self, image_dir, batches):
        super().__init__()
        self.image_dir = image_dir
        self.batches = batches
        self.current_batch = 0
        self.current_index = 0
        self.image_class = {}  # Store the class for each image

        # Create subdirectories if not exist
        for _, subdir, _ in KEY_ACTIONS.values():
            os.makedirs(os.path.join(image_dir, subdir), exist_ok=True)

        # Initialize the UI correctly
        self.initUI()

    def clear_layout(self):
        """Properly clear the current layout before loading a new batch."""
        layout = self.layout()
        if layout is not None:
            # Remove all widgets from the layout
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            # Remove the layout from the widget
            self.setLayout(None)
            # Delete the layout explicitly to avoid residual references
            del layout

    def initUI(self):
        """Initialize the user interface for the current batch."""
        self.clear_layout()

        # Get the current batch of images, sorted alphabetically
        self.images = sorted(self.batches[self.current_batch])

        # Extract batch identifiers for the title
        batch_example = self.images[0] if self.images else "unknown"
        match = re.match(r"m(\d+)_R_lines_(\d+)_chunk_\d+\.png", batch_example)
        if match:
            number1, number2 = match.groups()
            self.setWindowTitle(f"Batch {self.current_batch + 1}: mask {number1} line {number2}")
        else:
            self.setWindowTitle(f"Batch {self.current_batch + 1}: Unknown Format")

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
            pixmap = QPixmap(os.path.join(self.image_dir, image))
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
        if 0 <= self.current_index < len(self.labels):
            color = self.image_class.get(self.current_index, "transparent")
            self.labels[self.current_index].setStyleSheet(f"border: 2px solid {color};")
        self.current_index = new_index
        if 0 <= self.current_index < len(self.labels):
            self.labels[self.current_index].setStyleSheet("border: 2px solid black;")

    def classify_image(self, key):
        """Classify the currently selected image."""
        if key in KEY_ACTIONS:
            color, category, log_message = KEY_ACTIONS[key]
            filename = self.images[self.current_index]
            self.image_class[self.current_index] = color
            print(f"{filename} {log_message}")
            self.labels[self.current_index].setStyleSheet(f"border: 2px solid {color};")

            # Move to the next image safely
            next_index = min(self.current_index + 1, len(self.labels) - 1)
            self.update_selection(next_index)

    def move_images(self):
        """Move images to respective directories."""
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
        ctrl_pressed = event.modifiers() & Qt.ControlModifier

        if ctrl_pressed and key == Qt.Key_Space:
            for index in range(len(self.images)):
                self.image_class[index] = "green"
                filename = self.images[index]
                print(f"{filename} is glyph")
                self.labels[index].setStyleSheet("border: 2px solid green;")
            self.update_selection(0)
        elif key in KEY_ACTIONS:
            self.classify_image(key)
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            if len(self.image_class) < len(self.images):
                print("Not all images in the current batch are classified.")
                QMessageBox.warning(self, "Incomplete Batch", "Please classify all images before proceeding.")
                return
            self.move_images()
            self.current_batch += 1
            if self.current_batch >= len(self.batches):
                print("All images processed.")
                QMessageBox.information(self, "Completed", "All images have been classified.")
                QApplication.quit()
            else:
                self.initUI()
        elif key == Qt.Key_Escape:
            reply = QMessageBox.question(self, "Exit", "Are you sure you want to exit?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                QApplication.quit()
        elif key == Qt.Key_Left:
            self.update_selection(max(0, self.current_index - 1))
        elif key == Qt.Key_Right:
            self.update_selection(min(len(self.labels) - 1, self.current_index + 1))
        elif key == Qt.Key_Up:
            self.update_selection(max(0, self.current_index - self.max_col))
        elif key == Qt.Key_Down:
            self.update_selection(min(len(self.labels) - 1, self.current_index + self.max_col))

def group_files(files):
    grouped = []
    def key_func(filename):
        match = re.match(r"m(\d+)_R_lines_(\d+)_chunk_\d+\.png", filename)
        return (int(match.group(1)), int(match.group(2))) if match else (None, None)
    files.sort(key=key_func)
    for _, group in groupby(files, key=key_func):
        grouped.append(sorted(list(group)))
    return grouped

def main():
    print(f"Script version: {SCRIPT_VERSION}")
    image_dir = sys.argv[1]
    files = [f for f in os.listdir(image_dir) if f.lower().endswith('.png')]
    batches = group_files(files)

    app = QApplication(sys.argv)
    window = ImageGrid(image_dir, batches)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
