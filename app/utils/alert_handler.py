"""
Utility for displaying alerts in the GUI application.
"""

from PyQt5.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt

class AlertHandler:
    @staticmethod
    def show_error(message, title="Error"):
        """Show an error alert to the user."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    @staticmethod
    def show_info(message, title="Information"):
        """Show an info alert to the user."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

class LoadingDialog(QDialog):
    def __init__(self, message="Loading..."):
        super().__init__()
        self.setWindowTitle("Please Wait")
        self.setModal(True)
        layout = QVBoxLayout()
        self.label = QLabel(message)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)
        self.setFixedSize(300, 100)
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint | Qt.WindowTitleHint)