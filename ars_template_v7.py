import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from CopyTab import CopyHTMLTab
from SiteSelection import SiteSelectionTab
from GHTab import GHTab
from QTab import QTab
from WYExtremesTab import WYTab
from QRatingTab import QRatingTab

class ARSApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ARS- Automated Records System")
        self.setGeometry(100, 100, 1200, 800)
        self._create_tabs()
        self._connect_submission_button_to_other_tabs()
        self._place_tabs_into_central_box_widget()  

    def _create_tabs(self):
        """
        Method to create the Selection, GH, Rating, Q, and Copy tabs.
        """
        self.tabs_container = ARSApplication._create_tab_widget(11)
        self.site_select_tab = SiteSelectionTab()
        self.tabs_container.addTab(self.site_select_tab, "Site Select")
        
        self.gh_tab = GHTab()
        self.tabs_container.addTab(self.gh_tab, "Gage Height Record")

        self.QRating_tab = QRatingTab()
        self.tabs_container.addTab(self.QRating_tab, "Discharge Q/Ratings/Shifts")

        self.q_tab = QTab()
        self.tabs_container.addTab(self.q_tab, "Discharge Record")

        self.wy_tab = WYTab()
        self.tabs_container.addTab(self.wy_tab, "Water Year Extremes")
        
        self.copy_html_tab = CopyHTMLTab()
        self.tabs_container.addTab(self.copy_html_tab, "Copy HTML")
    
    @staticmethod
    def _create_tab_widget(font_size: int):
        """
        Helper method to create the container for the GH, Rating, Q, and Copy tabs.

        Args:
            font_size(int): Point size of the tab labels font
        """
        tab_widget = QTabWidget()
        tab_widget_font = tab_widget.font()
        tab_widget_font.setPointSize(font_size)
        tab_widget.setFont(tab_widget_font)

        return tab_widget
    
    def _connect_submission_button_to_other_tabs(self):
        """
        Helper method to connect the submission button on the site selection tab
        to the other tabs so that pressing it will update them accordingly.
        """
        self.site_select_tab.submit_button.successfulSubmissionSignal.connect(self.copy_html_tab.disable_enable_button)
        self.site_select_tab.submit_button.successfulSubmissionSignal.connect(self.gh_tab.setup_record_ui)
        self.site_select_tab.submit_button.successfulSubmissionSignal.connect(self.QRating_tab.setup_record_ui)
        self.site_select_tab.submit_button.successfulSubmissionSignal.connect(self.q_tab.setup_record_ui)
        self.site_select_tab.submit_button.successfulSubmissionSignal.connect(self.wy_tab.setup_record_ui)
    
    def _place_tabs_into_central_box_widget(self):
        """
        Helper method to setup the box widget contiaining the tabs_container
        """
        layout = QVBoxLayout()
        layout.addWidget(self.tabs_container)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    window = ARSApplication()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
