
from PyQt5.QtWidgets import QComboBox
from Text_Line import Text_Line


class ComboBox(QComboBox):
    def __init__(self, label: str, font_size: int, options: list[str], connecting_func = None):
        super().__init__()
        self.field = Text_Line(label, font_size)
        for option in options:
            self.addItem(option)
        if connecting_func != None:
            self.currentIndexChanged.connect(connecting_func)