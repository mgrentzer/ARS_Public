import SiteV3, Record
from datetime import datetime, date, timedelta
from API_Session_V3 import SynchronousAquariusAPISession
from PyQt5.QtWidgets import QScrollArea, QLineEdit, QDateEdit, QPushButton, QFormLayout
from PyQt5 import QtCore
from Text_Line import Text_Line
from User_Inputs import User_Inputs
from PyQt5.QtCore import QDate


class SiteSelectionTab(QScrollArea):
    """
    Class to represent the first tab for site selection. The tab will
    prompt for the user's site, their name, and date ranges for their record.
    A sumbit button will also be present to start the process of retrieving
    data from AQ.

    Args:
        user_inputs_obj(User_Inputs): Container for the user's input to be shared with other componenets
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """
        Setup user interface for the first screen
        """
        layout = QFormLayout()
        self.station = QLineEdit()
        station_font = self.station.font()
        station_font.setPointSize(10)
        self.station.setFont(station_font)
        
        self.author = QLineEdit()
        self.author.setText("Michael H. Grentzer")
        self.author.setFont(station_font)

        self.start_date = QDateEdit(self)
        self.start_date.setDate(date.today())
        self.start_date.setFont(station_font)

        self.end_date = QDateEdit(self)
        self.end_date.setDate(date.today())
        self.end_date.setFont(station_font)

        # This is temporary to so I don't have to keep entering data each time!
        self.update_user_inputs()

        fields = [
            ("Station #:", self.station),
            ("Author:", self.author),
            ("Start Date:", self.start_date),
            ("End Date:", self.end_date)
        ]

        for label_text, field_widget in fields:
            field_widget.setFixedWidth(200)
            if isinstance(field_widget, QDateEdit):
                field_widget.setCalendarPopup(True)  # Enable calendar popup
            
            # Update user_inputs container each time user finishes editing a input field
            field_widget.editingFinished.connect(self.warn_about_changes) 
            field_widget.setFixedHeight(40)
            layout.addRow(Text_Line(label_text, 11), field_widget)

        self.submit_button = SubmitButton()
        layout.addRow(self.submit_button)
        self.setLayout(layout)

    def warn_about_changes(self):
        if User_Inputs.successfulSubmissionCnt == 1 and User_Inputs.changesWarningCnt == 0:
            User_Inputs.changesWarningCnt += 1
            User_Inputs.warning_message("Warning: Changes will not take effect until resubmission.")

    def update_user_inputs(self):
        """
        Instance method to update the shared User Inputs object class whenever the
        user makes changes to the text and calandar/date fields. If there was a 
        successful data pull from AQ, a warning message will alert the user that
        they must click the resubmit button to update their end product.
        """
        
        new_start_date = self.start_date.date()
        User_Inputs.start_date = datetime(new_start_date.year(), new_start_date.month(), new_start_date.day())
        
        new_end_date = self.end_date.date()
        end_of_day = timedelta(hours=23, minutes=59, seconds=59)
        User_Inputs.end_date = datetime(new_end_date.year(), new_end_date.month(), new_end_date.day()) + end_of_day

        User_Inputs.site_no = self.station.text().strip()
        User_Inputs.author = self.author.text().strip()

class SubmitButton(QPushButton):
    """
    Class overriding the push button widget with extra functionality to check the user's
    field inputs and warn them if there are issues with them. It then requests data
    from AQ and will setup the UI tabs if all of the needed data is acquired.
    """
    successfulSubmissionSignal = QtCore.pyqtSignal()  # Define a custom signal

    def __init__(self):
        super().__init__("Submit")
        self.setFixedWidth(200)
        self.clicked.connect(self._submit)
        
    def _submit(self):
        """
        Method to perform the data retrieval request with the user's field inputs when
        the button is pushed.
        """
        self.parent().update_user_inputs()
        if not self._check_date_swap() and User_Inputs.valid_connection() and self._gather_preliminary_site_data():
            self._check_site()
        
    def _check_date_swap(self):
        """
        Method to check that the user's provided record start and end date are not swapped whereby
        the end date is before the start date.
        """
        if User_Inputs.start_date > User_Inputs.end_date:
            User_Inputs.critical_error_message("Start date cannot be later than end date.")
            return True
        
        return False

    def _gather_preliminary_site_data(self):
        """
        Helper method to attempt to retrieve the site data based on the user's input. Will throw
        an error message if the give a bad site number or if there's a connection issue. Will
        return True if site retrieval was successful and false if unsuccessful. Does not
        count as successful submission for data yet (not until we know there's data).
        """
        try:
            SynchronousAquariusAPISession.login()
            self.preliminary_users_record = Record.Record(User_Inputs.start_date, User_Inputs.end_date)
            self.preliminary_users_site = SiteV3.Site(User_Inputs.site_no)
            self.preliminary_users_site.gather_records_info_from_dates(User_Inputs.start_date, User_Inputs.end_date)
            SynchronousAquariusAPISession.logout()
            return True
        
        except Exception as e:
            print(str(e), e.__traceback__)
            if User_Inputs.valid_connection():
                User_Inputs.critical_error_message("Error: Invalid Site")
            return False

    def _check_site(self):
        """
        Check the preliminary site data for whether there is a gage height or elevation timeseries
        and whether said timeseries have any data during the user's stated period of record.
        """
        if len(self.preliminary_users_site.gage_height_timeseries_list) == 0:
            User_Inputs.critical_error_message("Error: No Gage Height or Elevation Timeseries Available")  # Display error message
        
        else:
            data_available = False
            for ts in self.preliminary_users_site.gage_height_timeseries_list:
                if(len(ts.record_dataset.data) > 0):
                    data_available = True

            if data_available == False:
                User_Inputs.critical_error_message("Error: No Gage Height or Elevation Data Available")  # Display error message
            else:
                # Now we have a successful submission of user's record info
                User_Inputs.successfulSubmissionCnt += 1
                User_Inputs.site = self.preliminary_users_site
                User_Inputs.record = self.preliminary_users_record
                self.successfulSubmissionSignal.emit()

