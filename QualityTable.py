from PyQt5.QtWidgets import QScrollArea, QComboBox, QTableWidget, QLineEdit, QDateEdit, QPushButton
from datetime import datetime, date

from PyQt5.QtWebEngineWidgets import QWebEngineView
from User_Inputs import User_Inputs
from html_table import html_table, html_table_row

class Quality_Table(QTableWidget):
    def __init__(self, table_name: str):
        super().__init__()
        self.name = table_name
        self.data_rows: list[quality_table_row] = []
        self.setFixedSize(880, 400)
        self._create_columns()

    def _create_columns(self):
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Period Start Date", "Period End Date", "Quality", "Comment(s)"])

        # Set column widths (adjust values as needed)
        self.setColumnWidth(0, 175)  # Period Start Date
        self.setColumnWidth(1, 175)  # Period End Date
        self.setColumnWidth(2, 100)  # Quality
        self.setColumnWidth(3, 400)  # Comment(s)
    
    def create_add_button(self):
        add_button = QPushButton("Add Entry")
        add_button.setFixedWidth(400)
        add_button.clicked.connect(self.add_entry_gh)
        return add_button
        
    def add_entry_gh(self):
        row_position = self.rowCount()
        self.insertRow(row_position)

        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDisplayFormat("yyyy-MM-dd")
        start_date.setDate(User_Inputs.start_date)
        
        end_date = QDateEdit()
        end_date.setDisplayFormat("yyyy-MM-dd")
        end_date.setCalendarPopup(True)
        end_date.setDate(User_Inputs.end_date)

        quality_combo = QComboBox()
        quality_combo.addItems(["Good", "Fair", "Poor"])

        comment_item = QLineEdit()  # Adding a QLineEdit for comments

        self.setCellWidget(row_position, 0, start_date)
        self.setCellWidget(row_position, 1, end_date)
        self.setCellWidget(row_position, 2, quality_combo)
        self.setCellWidget(row_position, 3, comment_item)

        # Update the data_rows list
        new_row = quality_table_row(start_date, end_date, quality_combo, comment_item)
        self.data_rows.append(new_row)

    def create_remove_button(self):
        remove_button = QPushButton("Remove Entry")
        remove_button.setFixedWidth(400)
        remove_button.clicked.connect(self.remove_entry_gh)
        return remove_button

    def remove_entry_gh(self):
        selected_row = self.currentRow()
        if selected_row >= 0:
            self.removeRow(selected_row)
            # Remove the corresponding data_row
            if selected_row < len(self.data_rows):
                del self.data_rows[selected_row]

    def return_html_table(self):
        table_header_row = html_table_row(["Period Start Date", "Period End Date", "Quality", "Comment(s)"])
        body_rows_list = []
        for data_row in self.data_rows:
            period_start_Qdate = data_row.start_date.date()
            period_start = date(period_start_Qdate.year(), period_start_Qdate.month(), period_start_Qdate.day())
            period_end_Qdate = data_row.end_date.date()
            period_end = date(period_end_Qdate.year(), period_end_Qdate.month(), period_end_Qdate.day())
            quality = data_row.quality.currentText()
            comments = data_row.comment.text()
            html_row = html_table_row([str(period_start), str(period_end), quality, comments])
            body_rows_list.append(html_row)
        quality_table_obj = html_table(table_header_row, body_rows_list, 580)
        
        return quality_table_obj.return_html()

class quality_table_row():
    def __init__(self, start_date,end_date, quality, comment):
        self.start_date = start_date
        self.end_date = end_date
        self.quality = quality
        self.comment = comment

class WebWindow(QScrollArea):
    def __init__(self, html: str, dimensions: list[int, int]):
        super().__init__()
        self.datum_web_view = QWebEngineView()
        self.datum_web_view.setZoomFactor(1.25)
        self.datum_web_view.setHtml(html)

        self.setWidget(self.datum_web_view)
        self.setWidgetResizable(True)
        self.setFixedSize(dimensions[0], dimensions[1])

    def return_update_button(self, func):
        update_button = QPushButton("Update")
        update_button.setFixedWidth(200)
        update_button.clicked.connect(func)
        return update_button

    def return_datum_update_button(self):
        update_button = QPushButton("Update")
        update_button.setFixedWidth(200)
        update_button.clicked.connect(self.update_datum_window)
        return update_button

