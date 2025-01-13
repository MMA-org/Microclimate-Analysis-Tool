class SidebarController:
    def __init__(self, main_window):
        self.main_window = main_window

        # Determine initial state based on sidebar visibility
        self.sidebar_expanded = True

        # Connect menu button for toggling sidebar
        self.main_window.menuButton.clicked.connect(self.toggle_sidebar)

        # Initialize buttons and their corresponding pages
        self.sidebar_buttons = {
            self.main_window.dataPageButton: 0,
            self.main_window.segmentPageButton: 1,
            self.main_window.analysisPageButton: 2,
            self.main_window.filesPageButton: 3,
        }

        # Connect sidebar buttons to their r    espective pages
        for button, page_index in self.sidebar_buttons.items():
            button.clicked.connect(lambda _, b=button, p=page_index: self.switch_page(p, b))

        # Set the default active page
        self.switch_page(0, self.main_window.dataPageButton)

    def toggle_sidebar(self):
        """Toggle the visibility of the sidebar."""
        sidebar = self.main_window.sidebarContainer

        # Toggle visibility
        self.sidebar_expanded = not self.sidebar_expanded
        sidebar.setVisible(self.sidebar_expanded)

    def switch_page(self, page_index, active_button):
        """Switch to the specified page and update button styles."""
        # Change to the selected page
        self.main_window.pagesContainer.setCurrentIndex(page_index)

        # Update button styles
        for button in self.sidebar_buttons.keys():
            button.setProperty("active", button == active_button)
            button.style().unpolish(button)
            button.style().polish(button)
