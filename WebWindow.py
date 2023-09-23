from PyQt5.QtWidgets import QScrollArea, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from User_Inputs import User_Inputs


class WebWindow(QScrollArea):
    def __init__(self, html: str, dimensions: list[int, int]):
        super().__init__()
        self.web_view = QWebEngineView()
        self.web_view.setZoomFactor(1.50)
        self.web_view.setHtml(html)

        self.setWidget(self.web_view)
        self.setWidgetResizable(True)
        self.setFixedSize(dimensions[0], dimensions[1])

    def return_update_button(self, func):
        update_button = QPushButton("Update")
        update_button.setFixedWidth(200)
        update_button.clicked.connect(func)
        return update_button

