import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

SCRIPT_VERSION = "2.2"

class ImageGrid(QWidget):
    def __init__(self, image_dir):
        super().__init__()
        self.setWindowTitle(f"Image Grid - {os.path.abspath(image_dir)}")
        self.setFocusPolicy(Qt.StrongFocus)  # Ensure the widget can capture keyboard events

        # Initialize navigation variables
        self.current_index = 0

        # Get PNG files sorted alphabetically
        self.images = sorted([f for f in os.listdir(image_dir) if f.lower().endswith('.png')])
        self.image_dir = image_dir

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
            self.labels[self.current_index].setStyleSheet("border: 2px solid transparent;")

        # Update current index
        self.current_index = new_index

        # Highlight the new selection
        if 0 <= self.current_index < len(self.labels):
            self.labels[self.current_index].setStyleSheet("border: 2px solid red;")

    def keyPressEvent(self, event):
        """Handle keyboard navigation and selection."""
        key = event.key()
        row = self.current_index // self.max_col
        col = self.current_index % self.max_col

        if key == Qt.Key_Left:
            new_index = max(0, self.current_index - 1)
        elif key == Qt.Key_Right:
            new_index = min(len(self.labels) - 1, self.current_index + 1)
        elif key == Qt.Key_Up:
            new_index = max(0, self.current_index - self.max_col)
        elif key == Qt.Key_Down:
            new_index = min(len(self.labels) - 1, self.current_index + self.max_col)
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            # Print the currently selected image
            print(f"Selected: {self.images[self.current_index]}")
            return
        else:
            # Ignore other keys
            return

        self.update_selection(new_index)

    def mousePressEvent(self, event):
        """Ensure the widget gains focus when clicked."""
        self.setFocus()

def main():
    print(f"Script version: {SCRIPT_VERSION}")

    if len(sys.argv) != 2:
        print("Usage: python image_grid.py <image_directory>")
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
