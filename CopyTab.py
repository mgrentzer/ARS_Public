from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton
from PyQt5 import QtCore
from User_Inputs import User_Inputs
import pyperclip

class CopyHTMLTab(QWidget):
    """
    Class object representing the Copy HTML tab which will simply
    have a big button for the user to press to copy the HTML
    code of their report to their clipboard.
    """
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.button = CopyButton()
        self.disable_enable_button()

        layout.addWidget(self.button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
        
    
    def disable_enable_button(self):
        """
        Class method to work as a socket to disable and enable the copy html button
        based on whether the user made a successful data retrieval from AQ. Won't enable
        until they got a retrieval with at least one gage height timeseries unit value.
        """
        if User_Inputs.successfulSubmissionCnt == 0:
            self.button.setEnabled(False)
        else:
            self.button.setEnabled(True)

class CopyButton(QPushButton):
    """
    Class to represent the button for copying the html report to the clipboard and all
    it's supporting functionality.
    """
    def __init__(self):
        super().__init__("Copy HTML")
        self.setFixedSize(150, 75)  # Set fixed width and height
        self.clicked.connect(self.copy)
    
    def copy(self):
        """
        Instance method to copy the user inputs and html documentation to
        the clipboard.
        """
        
        record = User_Inputs.record
        
        html = record.create_html_record(User_Inputs.site, User_Inputs)
        
        pyperclip.copy(html)
    
