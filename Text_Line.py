import sys, SiteV3, Record
from datetime import datetime, date
from API_Session_V3 import SynchronousAquariusAPISession
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSpacerItem, QScrollArea, QComboBox, QTableWidget, QWidget, QLabel, QLineEdit, QDateEdit, QTabWidget, QPushButton, QFormLayout, QMessageBox
from PyQt5 import QtCore
import pyperclip
from PyQt5.QtWebEngineWidgets import QWebEngineView

class Text_Line(QLabel):
    def __init__(self, text: str, font_size: int):
        super().__init__()
        self.setText(text)
        font = self.font()  # Get the current QFont object from the label
        font.setPointSize(font_size)  # Set the desired font size
        self.setFont(font)