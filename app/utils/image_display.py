import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QLineEdit
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

    def clear_layout(self, layout):
        """Remove all widgets from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())

    def remove_image(self, widget, image_path, image_paths, layout):
        """Remove a single image widget and rebuild the layout."""
        if image_path in image_paths:
            image_paths.remove(image_path)
            layout.removeWidget(widget)
            widget.deleteLater()

            # Rebuild the layout to ensure proper alignment
            self.clear_layout(layout)
            for index, path in enumerate(image_paths):
                row, col = divmod(index, 2)
                new_widget = self.create_image_widget(
                    path, show_year_input=True,
                    remove_callback=lambda w=widget, p=path: self.remove_image(w, p, image_paths, layout)
                )
                layout.addWidget(new_widget, row, col)
