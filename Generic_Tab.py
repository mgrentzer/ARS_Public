from API_Session_V3 import SynchronousAquariusAPISession
from PyQt5.QtWidgets import QScrollArea, QWidget, QLabel, QFormLayout
from PyQt5 import QtCore
from Text_Line import Text_Line
from User_Inputs import User_Inputs
from WebWindow import WebWindow


class Generic_Tab(QScrollArea):
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

    def setup_default_ui(self):
        """
        Method to setup the gage height record tab upon application's startup to
        be simply a box with the words  "No site data available."
        """
        self.layout = QFormLayout()
        self.layout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.first_label = Text_Line("No site data available.", 11)
        
        self.policy = self.first_label.sizePolicy()
        self.policy.setVerticalStretch(0) # Stops all of the elements from stretching! Moving around when you resize window.
        
        User_Inputs.size_policy = self.policy
        self.first_label.setSizePolicy(self.policy)
        self.layout.addRow(self.first_label)

        # Create a widget to hold the form layout
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.layout)
        self.setWidget(scroll_widget)
        self.setWidgetResizable(True)
    

    def setup_section(self, section_label, data_getter, data_creator, html_attribute, html_width=800, html_height=400):
        self._add_label(section_label)
        data_creator()
        html = getattr(User_Inputs.record, html_attribute)
        web_window = WebWindow(html, [html_width, html_height])
        web_window.setSizePolicy(self.policy)

        self.layout.addRow(web_window)
        update_function = lambda: self.update_section(data_getter, data_creator, web_window, html_attribute)
        self._add_update_button(web_window, update_function)

    def update_section(self, data_getter, data_creator, web_window, html_attribute):
        try:
            response = SynchronousAquariusAPISession.login()
            if int(response) >= 400:
                User_Inputs.critical_error_message(response.text)
                return False

            data_getter()
            data_creator()
            new_html = getattr(User_Inputs.record, html_attribute)
            web_window.web_view.setHtml(new_html)

            response = SynchronousAquariusAPISession.logout()
            if response >= 400:
                User_Inputs.critical_error_message(response.text)
                return False

        except Exception as e:
            print(str(e))
            User_Inputs.critical_error_message("Error: Cannot Connect to AQ\n\nCheck your connection and VPN.")
            return False

        return True

    def clear_tab(self):
        """
        Helper method to clear all of the contents of the tab so that it
        can be repopulated for the new sumbission's data.
        """
        for i in reversed(range(self.layout.count())): 
                self.layout.itemAt(i).widget().setParent(None)    
    
    def warn_about_updated_pages(self):
        """
        Helper method to notify the user that some of their previous inputs in
        the paragraph and table widgets will be removed because they are requesting
        a site with fewer gage height sensors.
        """
        lessTables = len(User_Inputs.gh_tables_list) > len(User_Inputs.site.gage_height_timeseries_list)

        if lessTables:
            User_Inputs.warning_message("The number of gage height timeseries has decreased, excess tables and paragraph boxes were removed with the remaining preserving your previous inputs.")

    def add_widget_spacer(self):
        """
        Helper method to simply two newlines to the field form
        """
        self.layout.addRow(QLabel(""))


    def _add_label(self, section_label):
        """
        Add the remove and add buttons to the bottom of the provided table.

        Args:
            section_label (str): The table section's label
        """
        label_line = Text_Line(section_label, 11)
        label_line.setSizePolicy(self.policy)
        self.layout.addRow(label_line)
    
    def _add_update_button(self, window, func):
        update_button = window.return_update_button(func)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()
    
    def _update_gh_ts(self):
        gh_ts_list = User_Inputs.site.gage_height_timeseries_list 
        for ts in gh_ts_list:
            ts.populate_datasets_for_records(User_Inputs.start_date, User_Inputs.end_date)
        
    def _update_q_ts(self):
        q_ts_list = User_Inputs.site.discharge_timeseries_list 
        for ts in q_ts_list:
            ts.populate_datasets_for_records(User_Inputs.start_date, User_Inputs.end_date)

