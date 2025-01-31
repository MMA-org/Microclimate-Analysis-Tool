import pytest
from PyQt5.QtWidgets import QApplication

@pytest.fixture(scope="session", autouse=True)
def app():
    "Ensure a QApplication instance is created for the test session."
    
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    yield app
    app.quit()
