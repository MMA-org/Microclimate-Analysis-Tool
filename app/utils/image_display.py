import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QLineEdit
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize


class ImageDisplayHandler:
    def create_image_widget(self, image_path, show_year_input=False):
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
        delete_button.clicked.connect(lambda: container.deleteLater())
        details_layout.addWidget(delete_button)

        # Image name
        image_name = QLabel(image_path.split("/")[-1])
        image_name.setMaximumWidth(200)
        details_layout.addWidget(image_name)

        # Optional year input
        if show_year_input:
            year_input = QLineEdit()
            year_input.setPlaceholderText("Year")
            year_input.setFixedWidth(100)
            year_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            details_layout.addWidget(year_input)

        container_layout.addWidget(details_container)
        return container

    def clear_layout(self, widget):
        """Remove all widgets and layouts from a container."""
        layout = widget.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear_layout(child.layout())

    def remove_image(self, image_path, image_paths, refresh_ui_callback):
        """Remove an image from the list and refresh the UI."""
        if image_path in image_paths:
            image_paths.remove(image_path)
            refresh_ui_callback()
