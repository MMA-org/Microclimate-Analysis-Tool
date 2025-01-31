"""
Utility for managing image display in the GUI application.
"""

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QLineEdit, QGridLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize


class ImageDisplayHandler:
    def create_image_widget(self, image_path, show_year_input=False, remove_callback=None):
        """Create a widget for an image with optional year input and delete button."""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignTop)

        # Image display
        image_label = QLabel()
        pixmap = QPixmap(image_path).scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(image_label)

        # Image details
        details_container = QWidget()
        details_layout = QHBoxLayout(details_container)
        details_layout.setSpacing(15)
        details_layout.setAlignment(Qt.AlignCenter)

        # Delete button
        delete_button = QPushButton()
        icon_path = os.path.join(os.path.dirname(__file__), "../../assets/icons/delete.svg")
        delete_button.setIcon(QIcon(icon_path))
        delete_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        delete_button.setIconSize(QSize(20, 20))
        delete_button.setStyleSheet("border: none;")
        delete_button.clicked.connect(lambda: remove_callback(container, image_path) if remove_callback else None)
        details_layout.addWidget(delete_button)

        # Image name
        image_name = QLabel(image_path.split("/")[-1])
        image_name.setMaximumWidth(200)
        image_name.setObjectName("imageName")
        details_layout.addWidget(image_name)

        # Optional year input
        if show_year_input:
            year_input = QLineEdit()
            year_input.setObjectName("yearInput")
            year_input.setPlaceholderText("Year")
            year_input.setFixedWidth(100)
            year_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            details_layout.addWidget(year_input)

        container_layout.addWidget(details_container)
        return container

    def clear_layout(self, layout):
        """Remove all widgets from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())

    def remove_image(self, widget, image_path, image_paths, layout, images_per_row):
        """Remove a single image widget and rebuild the layout."""
        if image_path in image_paths:
            image_paths.remove(image_path)
            layout.removeWidget(widget)
            widget.deleteLater()

            self.populate_scroll_area(layout.parentWidget(), image_paths, show_year_input=True, images_per_row=images_per_row)

    def populate_scroll_area(self, container, image_paths, show_year_input=False, images_per_row=2):
        """
        Add image widgets to the scroll area.

        Args:
            container (QWidget): The scroll area container for displaying images.
            image_paths (list): List of image paths to display.
            show_year_input (bool): Whether to include year input fields for images.
            images_per_row (int): Number of images to display per row.
        """
        layout = container.layout()
        if layout is None:
            layout = QGridLayout()
            container.setLayout(layout)

        self.clear_layout(layout)

        for index, image_path in enumerate(image_paths):
            widget = self.create_image_widget(
                image_path,
                show_year_input=show_year_input,
                remove_callback=lambda widget, path=image_path: self.remove_image(
                    widget, path, image_paths, layout, images_per_row
                ),
            )
            row, col = divmod(index, images_per_row)
            layout.addWidget(widget, row, col)

        if len(image_paths) % images_per_row != 0:
            last_row = len(image_paths) // images_per_row
            for col in range(len(image_paths) % images_per_row, images_per_row):
                spacer = QWidget()
                layout.addWidget(spacer, last_row, col)

    def get_images_with_years(self, container):
        """Retrieve image filenames and their associated years from the scroll area."""
        layout = container.layout()
        images_with_years = {}

        if not layout:
            return images_with_years

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if not widget:
                continue

            image_label = widget.findChild(QLabel, "imageName")
            year_input = widget.findChild(QLineEdit, "yearInput")

            if not image_label:  
                continue
            
            image_name = image_label.text()
            year_text = year_input.text().strip() if year_input else ""
            
            if year_text.isdigit():
                images_with_years[image_name] = int(year_text)

        return images_with_years


