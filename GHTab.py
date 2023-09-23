from API_Session_V3 import SynchronousAquariusAPISession
from PyQt5.QtWidgets import QScrollArea, QWidget, QLabel, QTextEdit, QFormLayout
from PyQt5 import QtCore
from Text_Line import Text_Line
from User_Inputs import User_Inputs
from WebWindow import WebWindow
from ComboBox import ComboBox
from Quality_Section import Quality_Section

class GHTab(QScrollArea):
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
        self.setup_default_ui()
        self.gh_quality_sections = []

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
    
    
    def setup_record_ui(self):
        """
        Upon having a successful submission/request for site data, this method
        will setup the gage height record tab with all the needed UI elements.
        If this is not the first setup, then the previous user data will be
        kept wherever possible.
        """
        firstSubmission = User_Inputs.successfulSubmissionCnt == 1

        if not firstSubmission:
            self.clear_tab()
            self.setup_default_ui()
            self.warn_about_updated_pages()
        
        self.setup_and_add_all_sections()

    def setup_and_add_all_sections(self):

        self.setup_special_notes_section()
    
        self.setup_section("Field Visits Section Preview",
                           lambda: User_Inputs.site._gather_field_visits(User_Inputs.start_date, User_Inputs.end_date),
                           lambda: User_Inputs.record.create_field_visits_table_section(User_Inputs.site.field_visits),
                           "field_visit_section")

        self.gh_quality_section = Quality_Section("Gage Height Quality Rating",
                                            User_Inputs.site.gage_height_timeseries_list, 
                                            User_Inputs.gh_tables_list,
                                            self.layout,
                                            self.policy)
        
        self.gh_quality_section.setup_quality_tables()

        self.setup_section("Datum Section Preview",
                            User_Inputs.site._gather_levels_description,
                            lambda: User_Inputs.record.create_datum_section(User_Inputs.site.levels_description),
                            "datum_section")

        self.setup_section("Checkbar Section Preview",
                           lambda: User_Inputs.site._gather_field_visits(User_Inputs.start_date, User_Inputs.end_date),
                           lambda: User_Inputs.record.create_checkbar_section(User_Inputs.site.field_visits, User_Inputs.site.sensors),
                           "checkbar_section")
        
        self.create_backup_view()

        self.setup_section("Ice Affected Section Preview",
                           self._update_gh_ts,
                           lambda: User_Inputs.record.create_ice_affected_section(User_Inputs.site.gage_height_timeseries_list),
                           "ice_section")

        self.setup_section("Edits Section Preview",
                           self._update_gh_ts,
                           lambda: User_Inputs.record.create_edits_section(User_Inputs.site.gage_height_timeseries_list),
                           "edits_section")

        self.setup_section("Gage Height Corrections Section Preview",
                           self._update_gh_ts,
                           lambda: User_Inputs.record.create_gh_correction_section(User_Inputs.site.gage_height_timeseries_list),
                           "gh_corrections_section")

        self.setup_section("Gaps Section Preview",
                           self._update_gh_ts,
                           lambda: User_Inputs.record.create_data_gaps_section(User_Inputs.site.gage_height_timeseries_list),
                           "data_gaps_section")

        self.setup_section("Other Gage Height Corrections Section Preview",
                           self._update_gh_ts,
                           lambda: User_Inputs.record.create_other_corrections_section(User_Inputs.site.gage_height_timeseries_list),
                           "other_gh_corrections_section")

        self.setup_section("Peak Verifications Section Preview",
                           self._update_gh_ts,
                           lambda: User_Inputs.record.create_peak_verifications_section(User_Inputs.site.field_visits),
                           "peak_verifications_section",
                           1000)
        
        self.create_peak_recorder_gh_view()
    

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
    
    def create_peak_recorder_gh_view(self):
        gh_ts_list = User_Inputs.site.gage_height_timeseries_list
        self.peak_verification_input_combo_box_array = []
        
        if len(gh_ts_list) == 1:
            only_combo_box = ComboBox("Peak Verified:", 11, ["Yes", "No"], None)
            only_combo_box.setSizePolicy(self.policy)
            only_combo_box.field.setSizePolicy(self.policy)
            only_combo_box.setFixedWidth(300)
            self.peak_verification_input_combo_box_array = [only_combo_box]
        
        if len(gh_ts_list) > 1:
            for ts in gh_ts_list:
                ts_combo = ComboBox(f"Peak Verified ({ts.TS_sublocation}): ", 11, ["Yes", "No"], None)
                ts_combo.setSizePolicy(self.policy)
                ts_combo.setFixedWidth(300)
                self.peak_verification_input_combo_box_array.append(ts_combo)
                
        self._add_label("Peak Recorder Section Preview") 

        for box in self.peak_verification_input_combo_box_array:
            self.layout.addRow(box.field, box)
        
        User_Inputs.record.create_peak_recorder_stage_section(gh_ts_list, self.peak_verification_input_combo_box_array)

        backup_html = User_Inputs.record.peak_recorder_stage_section
        self.peak_recorder_gh_web_window = WebWindow(backup_html, [1000, 400])
        self.peak_recorder_gh_web_window.setSizePolicy(self.policy)
    
        self.layout.addRow(self.peak_recorder_gh_web_window)
        
        self._add_update_button(self.peak_recorder_gh_web_window, self.update_peak_recorder_gh_window)  
        
    def update_peak_recorder_gh_window(self):
        try:
            response = SynchronousAquariusAPISession.login()  # Capture the response
            if int(response) >= 400:  # Check for error status codes
                User_Inputs.critical_error_message(response.text)  # Display error message
                return False

            else:
                gh_ts_list = User_Inputs.site.gage_height_timeseries_list 
                for ts in gh_ts_list:
                    ts.populate_datasets_for_records(User_Inputs.start_date, User_Inputs.end_date)
                response = SynchronousAquariusAPISession.logout()  # Capture the response
                User_Inputs.record.create_peak_recorder_stage_section(gh_ts_list, self.peak_verification_input_combo_box_array)
                new_html = User_Inputs.record.peak_recorder_stage_section
                self.peak_recorder_gh_web_window.web_view.setHtml(new_html)
                
                if response >= 400:  # Check for error status codes
                    User_Inputs.critical_error_message(response.text)  # Display error message
                    return False
        
        except Exception as e:
            print(str(e.with_traceback))
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

    
    def update_user_inputs(self):
        """
        Instance method to update the shared User Inputs object class whenever the
        user makes changes to the text and calandar/date fields. If there was a 
        successful data pull from AQ, a warning message will alert the user that
        they must click the resubmit button to update their end product.
        """
        
        User_Inputs.special_notes = self.special_notes_text_box.toPlainText()


    def setup_special_notes_section(self):
        """
        Method to add the special notes section to the gage height tab.
        """
        self.first_label.setText("Special Notes Section (Optional)")
        self.special_notes_text_box = QTextEdit()
        self.special_notes_text_box.setSizePolicy(self.policy)
        self.special_notes_text_box.setFixedSize(700, 200)
        self.special_notes_text_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.special_notes_text_box.textChanged.connect(self.update_user_inputs)

        if User_Inputs.successfulSubmissionCnt > 1:
            self.special_notes_text_box.setText(User_Inputs.special_notes)

        self.layout.addRow(self.special_notes_text_box)
        self.add_widget_spacer()


    def create_backup_view(self):
        gh_ts_list = User_Inputs.site.gage_height_timeseries_list
        self.edl_data_condition_combo_box_array = []
        
        if len(gh_ts_list) == 1:
            only_combo_box = ComboBox("Archival Status:", 11, ["Archived Properly", "Partially Archived", "Not Archived Properly"], None)
            only_combo_box.setSizePolicy(self.policy)
            only_combo_box.field.setSizePolicy(self.policy)
            only_combo_box.setFixedWidth(300)
            self.edl_data_condition_combo_box_array = [only_combo_box]
        
        if len(gh_ts_list) > 1:
            for ts in gh_ts_list:
                name = f"Archival Status: ({ts.TS_sublocation})"
                ts_combo = ComboBox(name, 11, ["Archived Properly", "Partially Archived", "Not Archived Properly"], None)
                ts_combo.setSizePolicy(self.policy)
                ts_combo.setFixedWidth(300)
                self.edl_data_condition_combo_box_array.append(ts_combo)
                
        self._add_label("Backup Data Section Preview") 
        
        for box in self.edl_data_condition_combo_box_array:
            self.layout.addRow(box.field, box)
        User_Inputs.record.create_backup_data_section(gh_ts_list, self.edl_data_condition_combo_box_array)

        backup_html = User_Inputs.record.backup_data_section
        self.backup_web_window = WebWindow(backup_html, [800, 400])
        self.backup_web_window.setSizePolicy(self.policy)
    
        self.layout.addRow(self.backup_web_window)

        self._add_update_button(self.backup_web_window, self.update_backup_window)
        
    def update_backup_window(self):
        try:
            response = SynchronousAquariusAPISession.login()  # Capture the response
            if int(response) >= 400:  # Check for error status codes
                User_Inputs.critical_error_message(response.text)  # Display error message
                return False

            else:
                gh_ts_list = User_Inputs.site.gage_height_timeseries_list 
                for ts in gh_ts_list:
                    ts.populate_datasets_for_records(User_Inputs.start_date, User_Inputs.end_date)
                response = SynchronousAquariusAPISession.logout()  # Capture the response
                User_Inputs.record.create_backup_data_section(gh_ts_list, self.edl_data_condition_combo_box_array)
                new_html = User_Inputs.record.backup_data_section
                self.backup_web_window.web_view.setHtml(new_html)
                
                if response >= 400:  # Check for error status codes
                    User_Inputs.critical_error_message(response.text)  # Display error message
                    return False
        
        except Exception as e:
            print(str(e.with_traceback))
            User_Inputs.critical_error_message("Error: Cannot Connect to AQ\n\nCheck your connection and VPN.")
            return False

        return True

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

