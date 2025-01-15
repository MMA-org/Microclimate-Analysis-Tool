from PyQt5.QtWidgets import QMessageBox

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
        """Show an informational alert to the user."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()
