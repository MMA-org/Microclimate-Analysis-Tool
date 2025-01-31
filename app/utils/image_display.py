"""
Utility for managing image display in the GUI application.
"""

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QLineEdit, QGridLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize


class ImageDisplayHandler:
    "Handles displaying images dynamically with optional year inputs and deletion support."

    def create_image_widget(self, image_path, show_year_input=False, remove_callback=None):
        "Create a widget for displaying an image with optional year input and delete button."

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignTop)

        # Image display
        image_label = QLabel()
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # Image details (filename, delete button, optional year input)
        details_layout = QHBoxLayout()
        details_layout.setSpacing(15)
        details_layout.setAlignment(Qt.AlignCenter)

        delete_button = self._create_delete_button(remove_callback, container, image_path)
        details_layout.addWidget(delete_button)

        image_name = QLabel(os.path.basename(image_path))
        image_name.setMaximumWidth(200)
        image_name.setObjectName("imageName")
        details_layout.addWidget(image_name)

        if show_year_input:
            year_input = self._create_year_input()
            details_layout.addWidget(year_input)

        layout.addLayout(details_layout)
        return container

    def _create_delete_button(self, remove_callback, container, image_path):
        "Create and return a delete button."

        button = QPushButton()
        icon_path = os.path.join(os.path.dirname(__file__), "../../assets/icons/delete.svg")
        button.setIcon(QIcon(icon_path))
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setIconSize(QSize(20, 20))
        button.setStyleSheet("border: none;")

        if remove_callback:
            button.clicked.connect(lambda: remove_callback(container, image_path))

        return button

    def _create_year_input(self):
        "Create and return a QLineEdit for year input."

        year_input = QLineEdit()
        year_input.setObjectName("yearInput")
        year_input.setPlaceholderText("Year")
        year_input.setFixedWidth(100)
        year_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        return year_input

    def clear_layout(self, layout):
        "Remove all widgets from a given layout."

        if not layout:
            return
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

            elif item.layout():
                self.clear_layout(item.layout())

    def remove_image(self, widget, image_path, image_paths, layout, images_per_row):
        "Remove an image widget and refresh the scroll area."

        if image_path in image_paths:
            image_paths.remove(image_path)
            layout.removeWidget(widget)
            widget.deleteLater()
            self.populate_scroll_area(layout.parentWidget(), image_paths, show_year_input=True, images_per_row=images_per_row)

    def populate_scroll_area(self, container, image_paths, show_year_input=False, images_per_row=2):
        "Populate the scroll area with image widgets."

        layout = container.layout() or QGridLayout()
        container.setLayout(layout)

        self.clear_layout(layout)

        for index, image_path in enumerate(image_paths):
            widget = self.create_image_widget(
                image_path,
                show_year_input=show_year_input,
                remove_callback=lambda w, p=image_path: self.remove_image(w, p, image_paths, layout, images_per_row),
            )
            row, col = divmod(index, images_per_row)
            layout.addWidget(widget, row, col)

    def get_images_with_years(self, container):
        "Retrieve image filenames and their associated years from the scroll area."

        layout = container.layout()
        if not layout:
            return {}

        images_with_years = {}
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if not widget:
                continue

            image_label = widget.findChild(QLabel, "imageName")
            year_input = widget.findChild(QLineEdit, "yearInput")

            if image_label and year_input and year_input.text().strip().isdigit():
                images_with_years[image_label.text()] = int(year_input.text().strip())

        return images_with_years
