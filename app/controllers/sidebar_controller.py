"""
Sidebar controller for managing the sidebar navigation in the GUI application.
"""

class SidebarController:
    """
    This class handles the behavior of the sidebar, including toggling its visibility,
    connecting buttons to their respective pages, and updating active button styles.

    Args:
        main_window (QMainWindow): The main application window containing sidebar and pages.

    Attributes:
        main_window (QMainWindow): Reference to the main window.
        sidebar_expanded (bool): Tracks whether the sidebar is currently expanded.
        sidebar_buttons (dict): Maps sidebar buttons to their corresponding page indices.
    """

    def __init__(self, main_window):
        self.main_window = main_window

        self.sidebar_expanded = True

        self.main_window.menuButton.clicked.connect(self.toggle_sidebar)

        self.sidebar_buttons = {
            self.main_window.dataPageButton: 0,
            self.main_window.segmentPageButton: 1,
            self.main_window.analysisPageButton: 2,
        }

        for button, page_index in self.sidebar_buttons.items():
            button.clicked.connect(lambda _, b=button, p=page_index: self.switch_page(p, b))

        self.switch_page(0, self.main_window.dataPageButton)

    def toggle_sidebar(self):
        """
        Toggle the visibility of the sidebar.
        This method changes the visibility of the sidebar container by inverting the current state
        of `sidebar_expanded` and updates the UI accordingly.
        """
        sidebar = self.main_window.sidebarContainer

        self.sidebar_expanded = not self.sidebar_expanded
        sidebar.setVisible(self.sidebar_expanded)

    def switch_page(self, page_index, active_button):
        """
        Switch to the specified page and update button styles.
        This method updates the current page in the `pagesContainer` and ensures that the active
        button is visually highlighted.
        """
        self.main_window.pagesContainer.setCurrentIndex(page_index)

        for button in self.sidebar_buttons.keys():
            button.setProperty("active", button == active_button)
            button.style().unpolish(button)
            button.style().polish(button)
