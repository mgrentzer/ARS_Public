from API_Session_V3 import SynchronousAquariusAPISession
from PyQt5.QtWidgets import QScrollArea, QWidget, QLabel, QLineEdit, QFormLayout
from PyQt5 import QtCore
from Text_Line import Text_Line
from User_Inputs import User_Inputs
from QualityTable import Quality_Table
from WebWindow import WebWindow
from ComboBox import ComboBox

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


    def add_widget_spacer(self):
        """
        Helper method to simply two newlines to the field form
        """
        self.layout.addRow(QLabel(""))

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
        
        self.setup_special_notes_section()
        self.setup_field_visits_table()
        self.setup_gh_quality_tables()
        self.add_datum_view()
        self.create_checkbar_view()
        self.create_backup_view()
        self.create_ice_section()
        self.create_edits_section()
        self.create_gh_corrections_section()
        self.create_gaps_section()
        self.create_other_gh_corrections_section()
        self.create_peak_verification_section()
        # self.create_peak_recorder_gh_view()


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
        lessTables = len(User_Inputs.parameter_tables_list) > len(User_Inputs.site.gage_height_timeseries_list)

        if lessTables:
            User_Inputs.warning_message("The number of gage height timeseries has decreased, excess tables and paragraph boxes were removed with the remaining preserving your previous inputs.")

    def setup_gh_quality_tables(self):
        """
        Method to add the gage height quality tables dynamically to the gage height
        tab based upon however many sensor exist at the site which was requested.
        """
        site_gh_ts_list = User_Inputs.site.gage_height_timeseries_list      

        first_run = len(User_Inputs.parameter_tables_list) == 0
        one_table = len(site_gh_ts_list) == 1
        multiple_tables = len(site_gh_ts_list) > 1
        same_number_of_tables = len(site_gh_ts_list) == len(User_Inputs.parameter_tables_list) == 1
        more_tables =  len(site_gh_ts_list) > len(User_Inputs.parameter_tables_list)
        less_tables =  len(site_gh_ts_list) < len(User_Inputs.parameter_tables_list)

        if first_run and one_table:
            self._add_one_table()  

        elif first_run and multiple_tables:
            self._add_multiple_tables()

        elif not first_run and same_number_of_tables and one_table:
            self._restore_the_old_table()

        elif not first_run and same_number_of_tables and not one_table:
            self._update_multiple_table_labels()

        elif more_tables:
            self._add_more_tables_and_update_labels()
        
        elif less_tables:
            self._remove_extra_tables_update_labels()

    def _add_one_table(self):
        ts_label = QLabel("Gage Height Quality Rating")
        ts_label.setSizePolicy(self.policy)

        self.layout.addRow(ts_label)

        gh_table = Quality_Table("")
        gh_table.setSizePolicy(self.policy)
        User_Inputs.parameter_tables_list.append(gh_table)
        
        add_button = gh_table.create_add_button()
        remove_button = gh_table.create_remove_button()
        add_button.setSizePolicy(self.policy)
        remove_button.setSizePolicy(self.policy)

        self.layout.addRow(gh_table)
        self.layout.addRow(add_button, remove_button)  
        self.add_widget_spacer()    

    def _add_multiple_tables(self):
        for gh_ts in User_Inputs.site.gage_height_timeseries_list:
            ts_label = QLabel(f"Gage Height Quality Rating ({gh_ts.TS_identifier})")
            self.layout.addRow(ts_label)

            gh_table = Quality_Table(f"{gh_ts.TS_sublocation}")            
            User_Inputs.parameter_tables_list.append(gh_table)
            add_button = gh_table.create_add_button()
            remove_button = gh_table.create_remove_button()

            self.layout.addRow(gh_table)
            self.layout.addRow(add_button, remove_button)  
            self.add_widget_spacer()
    
    def _restore_the_old_table(self):
        ts_label = QLabel("Gage Height Quality Rating")
        ts_label.setSizePolicy(self.policy)

        self.layout.addRow(ts_label)

        gh_table = User_Inputs.parameter_tables_list[0]
        gh_table.setSizePolicy(self.policy)

        
        add_button = gh_table.create_add_button()
        remove_button = gh_table.create_remove_button()
        add_button.setSizePolicy(self.policy)
        remove_button.setSizePolicy(self.policy)

        self.layout.addRow(gh_table)
        self.layout.addRow(add_button, remove_button)  
        self.add_widget_spacer()

        User_Inputs.parameter_tables_list = []
        User_Inputs.parameter_tables_list.append(gh_table)

    def _update_multiple_table_labels(self):
        new_gh_tables = []
        for gh_ts, old_gh_table in zip(User_Inputs.site.gage_height_timeseries_list, User_Inputs.parameter_tables_list):
            ts_label = QLabel(f"Gage Height Quality Rating ({gh_ts.TS_identifier})")
            self.layout.addRow(ts_label)
            old_gh_table.setSizePolicy(self.policy)
            new_gh_tables.append(old_gh_table)
            add_button = old_gh_table.create_add_button()
            remove_button = old_gh_table.create_remove_button()
            add_button.setSizePolicy(self.policy)
            remove_button.setSizePolicy(self.policy)
            self.layout.addRow(old_gh_table)
            self.layout.addRow(add_button, remove_button)  
            self.add_widget_spacer()
            User_Inputs.parameter_tables_list = new_gh_tables

    def _add_more_tables_and_update_labels(self):
        new_gh_tables = []
        for old_gh_index, old_gh_table in enumerate(User_Inputs.parameter_tables_list):
            ts_label = QLabel(f"Gage Height Quality Rating ({User_Inputs.site.gage_height_timeseries_list[old_gh_index].TS_identifier})")
            self.layout.addRow(ts_label)
            old_gh_table.setSizePolicy(self.policy)
            new_gh_tables.append(old_gh_table)
            add_button = old_gh_table.create_add_button()
            remove_button = old_gh_table.create_remove_button()
            add_button.setSizePolicy(self.policy)
            remove_button.setSizePolicy(self.policy)
            self.layout.addRow(old_gh_table)
            self.layout.addRow(add_button, remove_button)  
            self.add_widget_spacer()
        
        for new_site_ts_index in range(len(User_Inputs.parameter_tables_list), len(User_Inputs.site.gage_height_timeseries_list)):
            new_ts = User_Inputs.site.gage_height_timeseries_list[new_site_ts_index]
            
            ts_label = QLabel("Gage Height Quality Rating")
            if len(User_Inputs.site.gage_height_timeseries_list) > 1:
                ts_label = QLabel(f"Gage Height Quality Rating ({new_ts.TS_identifier})")
            
            self.layout.addRow(ts_label)

            gh_table = Quality_Table(f"{new_ts.TS_sublocation}")            
            new_gh_tables.append(gh_table)
            add_button = gh_table.create_add_button()
            remove_button = gh_table.create_remove_button()

            self.layout.addRow(gh_table)
            self.layout.addRow(add_button, remove_button)  
            self.add_widget_spacer()
        
        User_Inputs.parameter_tables_list = new_gh_tables

    def _remove_extra_tables_update_labels(self):
        new_gh_tables = []
        for old_gh_index, old_gh_table in enumerate(User_Inputs.parameter_tables_list):
            if old_gh_index < len(User_Inputs.site.gage_height_timeseries_list):
                ts_label = QLabel(f"Gage Height Quality Rating ({User_Inputs.site.gage_height_timeseries_list[old_gh_index].TS_identifier})")
                self.layout.addRow(ts_label)
                old_gh_table.setSizePolicy(self.policy)
                new_gh_tables.append(old_gh_table)
                add_button = old_gh_table.create_add_button()
                remove_button = old_gh_table.create_remove_button()
                add_button.setSizePolicy(self.policy)
                remove_button.setSizePolicy(self.policy)
                self.layout.addRow(old_gh_table)
                self.layout.addRow(add_button, remove_button)  
                self.add_widget_spacer()
        
        User_Inputs.parameter_tables_list = new_gh_tables

    def update_user_inputs(self):
        """
        Instance method to update the shared User Inputs object class whenever the
        user makes changes to the text and calandar/date fields. If there was a 
        successful data pull from AQ, a warning message will alert the user that
        they must click the resubmit button to update their end product.
        """
        
        User_Inputs.special_notes = self.text_box.text()

    def setup_special_notes_section(self):
        """
        Method to add the special notes section to the gage height tab.
        """
        self.first_label.setText("Special Notes Section (Optional)")
        self.text_box = QLineEdit()
        self.text_box.setSizePolicy(self.policy)
        self.text_box.setFixedSize(700, 200)
        self.text_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.text_box.editingFinished.connect(self.update_user_inputs)

        if User_Inputs.successfulSubmissionCnt > 1:
            self.text_box.setText(User_Inputs.special_notes)

        self.layout.addRow(self.text_box)
        self.add_widget_spacer()
    
    
    def setup_field_visits_table(self):
        field_visits_label = Text_Line("Field Visits Section Preview", 11) 
        field_visits_label.setSizePolicy(self.policy)
        self.layout.addRow(field_visits_label)

        User_Inputs.record.create_field_visits_table_section(User_Inputs.site.field_visits)
        field_visit_table_html = User_Inputs.record.field_visit_section
        self.field_visit_web_window = WebWindow(field_visit_table_html, [800, 400])
        self.field_visit_web_window.setSizePolicy(self.policy)
        
        self.layout.addRow(self.field_visit_web_window)
        update_button = self.field_visit_web_window.return_update_button(self.update_field_visits_table)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()
    
    def update_field_visits_table(self):
        try:
            response = SynchronousAquariusAPISession.login()  # Capture the response
            if int(response) >= 400:  # Check for error status codes
                User_Inputs.critical_error_message(response.text)  # Display error message
                return False

            else:
                User_Inputs.site._gather_field_visits(User_Inputs.start_date, User_Inputs.end_date)
                User_Inputs.record.create_field_visits_table_section(User_Inputs.site.field_visits)
                new_html = User_Inputs.record.field_visit_section
                self.field_visit_web_window.web_view.setHtml(new_html)
                response = SynchronousAquariusAPISession.logout()  # Capture the response
                if response >= 400:  # Check for error status codes
                    User_Inputs.critical_error_message(response.text)  # Display error message
                    return False
        
        except Exception as e:
            print(str(e))
            User_Inputs.critical_error_message("Error: Cannot Connect to AQ\n\nCheck your connection and VPN.")
            return False

        return True

    def add_datum_view(self):
        datum_section_label = Text_Line("Datum Section Preview", 11) 
        datum_section_label.setSizePolicy(self.policy)
        self.layout.addRow(datum_section_label)

        User_Inputs.record.create_datum_section(User_Inputs.site.levels_description)
        datum_html = User_Inputs.record.datum_section
        self.datum_web_window = WebWindow(datum_html, [800, 200])
        self.datum_web_window.setSizePolicy(self.policy)
        
        self.layout.addRow(self.datum_web_window)
        update_button = self.datum_web_window.return_update_button(self.update_datum_window)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()
    
    def update_datum_window(self):
        User_Inputs.site._gather_levels_description()
        User_Inputs.record.create_datum_section(User_Inputs.site.levels_description)
        new_html = User_Inputs.record.datum_section
        self.datum_web_window.web_view.setHtml(new_html)

    
    def create_checkbar_view(self):
        if User_Inputs.site.has_wwg():
            field_visits = User_Inputs.site.field_visits
            sensors_list = User_Inputs.site.sensors

            checkbar_section_label = Text_Line("Checkbar Section Preview", 11) 
            checkbar_section_label.setSizePolicy(self.policy)
            self.layout.addRow(checkbar_section_label)

            User_Inputs.record.create_checkbar_section(field_visits, sensors_list)
            checkbar_html = User_Inputs.record.checkbar_section
            self.checkbar_web_window = WebWindow(checkbar_html, [800, 400])
            self.checkbar_web_window.setSizePolicy(self.policy)
            
            self.layout.addRow(self.checkbar_web_window)
            update_button = self.checkbar_web_window.return_update_button(self.update_checkbar_window)
            update_button.setSizePolicy(self.policy)
            self.layout.addRow(update_button)
            self.add_widget_spacer()
    
    def update_checkbar_window(self):
        try:
            response = SynchronousAquariusAPISession.login()  # Capture the response
            if int(response) >= 400:  # Check for error status codes
                User_Inputs.critical_error_message(response.text)  # Display error message
                return False

            else:
                field_visits = User_Inputs.site.field_visits
                sensors_list = User_Inputs.site.sensors
                User_Inputs.site._gather_field_visits(User_Inputs.start_date, User_Inputs.end_date)
                User_Inputs.record.create_checkbar_section(field_visits, sensors_list)
                new_html = User_Inputs.record.checkbar_section
                self.checkbar_web_window.web_view.setHtml(new_html)
                response = SynchronousAquariusAPISession.logout()  # Capture the response
                if response >= 400:  # Check for error status codes
                    User_Inputs.critical_error_message(response.text)  # Display error message
                    return False
            return True
        
        except Exception as e:
            print(str(e))
            User_Inputs.critical_error_message("Error: Cannot Connect to AQ\n\nCheck your connection and VPN.")
            return False
                
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
                
        ts_backup_label = Text_Line("Backup Data Section Preview", 11) 
        ts_backup_label.setSizePolicy(self.policy)
        self.layout.addRow(ts_backup_label)
        for box in self.edl_data_condition_combo_box_array:
            self.layout.addRow(box.field, box)
        User_Inputs.record.create_backup_data_section(gh_ts_list, self.edl_data_condition_combo_box_array)

        backup_html = User_Inputs.record.backup_data_section
        self.backup_web_window = WebWindow(backup_html, [800, 400])
        self.backup_web_window.setSizePolicy(self.policy)
    
        self.layout.addRow(self.backup_web_window)
        update_button = self.backup_web_window.return_update_button(self.update_backup_window)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()    
        
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

    def create_ice_section(self):
        gh_ts_list = User_Inputs.site.gage_height_timeseries_list
                
        ts_ice_label = Text_Line("Ice Affected Section Preview", 11) 
        ts_ice_label.setSizePolicy(self.policy)
        self.layout.addRow(ts_ice_label)
        User_Inputs.record.create_ice_affected_section(gh_ts_list)

        ice_html = User_Inputs.record.ice_section
        self.ice_web_window = WebWindow(ice_html, [800, 400])
        self.ice_web_window.setSizePolicy(self.policy)
    
        self.layout.addRow(self.ice_web_window)
        update_button = self.ice_web_window.return_update_button(self.update_ice_section)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()
    
    def update_ice_section(self):
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
                User_Inputs.record.create_ice_affected_section(gh_ts_list)
                new_html = User_Inputs.record.ice_section
                self.ice_web_window.web_view.setHtml(new_html)
                
                if response >= 400:  # Check for error status codes
                    User_Inputs.critical_error_message(response.text)  # Display error message
                    return False
        
        except Exception as e:
            print(str(e.with_traceback))
            User_Inputs.critical_error_message("Error: Cannot Connect to AQ\n\nCheck your connection and VPN.")
            return False

        return True

    def create_edits_section(self):
        gh_ts_list = User_Inputs.site.gage_height_timeseries_list
                
        ts_edits_label = Text_Line("Edits Section Preview", 11) 
        ts_edits_label.setSizePolicy(self.policy)
        self.layout.addRow(ts_edits_label)
        User_Inputs.record.create_edits_section(gh_ts_list)

        edits_html = User_Inputs.record.edits_section
        self.edits_web_window = WebWindow(edits_html, [800, 400])
        self.edits_web_window.setSizePolicy(self.policy)
    
        self.layout.addRow(self.edits_web_window)
        update_button = self.edits_web_window.return_update_button(self.update_edits_section)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()
    
    def update_edits_section(self):
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
                User_Inputs.record.create_edits_section(gh_ts_list)
                new_html = User_Inputs.record.edits_section
                self.edits_web_window.web_view.setHtml(new_html)
                
                if response >= 400:  # Check for error status codes
                    User_Inputs.critical_error_message(response.text)  # Display error message
                    return False
        
        except Exception as e:
            print(str(e.with_traceback))
            User_Inputs.critical_error_message("Error: Cannot Connect to AQ\n\nCheck your connection and VPN.")
            return False

        return True

    def create_gh_corrections_section(self):
        gh_ts_list = User_Inputs.site.gage_height_timeseries_list
                
        ts_gh_corr_label = Text_Line("Gage Height Corrections Section Preview", 11) 
        ts_gh_corr_label.setSizePolicy(self.policy)
        self.layout.addRow(ts_gh_corr_label)
        User_Inputs.record.create_gh_correction_section(gh_ts_list)
        gh_corr_html = User_Inputs.record.gh_corrections_section
        self.gh_corr_web_window = WebWindow(gh_corr_html, [800, 400])
        self.gh_corr_web_window.setSizePolicy(self.policy)
    
        self.layout.addRow(self.gh_corr_web_window)
        update_button = self.gh_corr_web_window.return_update_button(self.update_gh_corr_section)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()
    
    def update_gh_corr_section(self):
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
                User_Inputs.record.create_gh_correction_section(gh_ts_list)
                new_html = User_Inputs.record.gh_corrections_section
                self.gh_corr_web_window.web_view.setHtml(new_html)
                
                if response >= 400:  # Check for error status codes
                    User_Inputs.critical_error_message(response.text)  # Display error message
                    return False
        
        except Exception as e:
            print(str(e.with_traceback))
            User_Inputs.critical_error_message("Error: Cannot Connect to AQ\n\nCheck your connection and VPN.")
            return False

        return True

    def create_gaps_section(self):
        gh_ts_list = User_Inputs.site.gage_height_timeseries_list
                
        ts_gaps_label = Text_Line("Gaps Section Preview", 11) 
        ts_gaps_label.setSizePolicy(self.policy)
        self.layout.addRow(ts_gaps_label)
        User_Inputs.record.create_data_gaps_section(gh_ts_list)
        gh_gaps_html = User_Inputs.record.data_gaps_section
        self.gh_gaps_web_window = WebWindow(gh_gaps_html, [800, 400])
        self.gh_gaps_web_window.setSizePolicy(self.policy)
    
        self.layout.addRow(self.gh_gaps_web_window)
        update_button = self.gh_gaps_web_window.return_update_button(self.update_gaps_section)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()
    
    def update_gaps_section(self):
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
                User_Inputs.record.create_data_gaps_section(gh_ts_list)
                new_html = User_Inputs.record.data_gaps_section
                self.gh_gaps_web_window.web_view.setHtml(new_html)
                
                if response >= 400:  # Check for error status codes
                    User_Inputs.critical_error_message(response.text)  # Display error message
                    return False
        
        except Exception as e:
            print(str(e.with_traceback))
            User_Inputs.critical_error_message("Error: Cannot Connect to AQ\n\nCheck your connection and VPN.")
            return False

        return True

    def create_other_gh_corrections_section(self):
        gh_ts_list = User_Inputs.site.gage_height_timeseries_list
                
        ts_gh_corr_label = Text_Line("Other Gage Height Corrections Section Preview", 11) 
        ts_gh_corr_label.setSizePolicy(self.policy)
        self.layout.addRow(ts_gh_corr_label)
        User_Inputs.record.create_other_corrections_section(gh_ts_list)
        other_gh_corr_html = User_Inputs.record.other_gh_corrections_section
        self.other_gh_corr_web_window = WebWindow(other_gh_corr_html, [800, 400])
        self.other_gh_corr_web_window.setSizePolicy(self.policy)
    
        self.layout.addRow(self.other_gh_corr_web_window)
        update_button = self.other_gh_corr_web_window.return_update_button(self.update_other_gh_corr_section)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()
    
    def update_other_gh_corr_section(self):
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
                User_Inputs.record.create_other_corrections_section(gh_ts_list)
                new_html = User_Inputs.record.other_gh_corrections_section
                self.other_gh_corr_web_window.web_view.setHtml(new_html)
                
                if response >= 400:  # Check for error status codes
                    User_Inputs.critical_error_message(response.text)  # Display error message
                    return False
        
        except Exception as e:
            print(str(e.with_traceback))
            User_Inputs.critical_error_message("Error: Cannot Connect to AQ\n\nCheck your connection and VPN.")
            return False

        return True
    
    def create_peak_verification_section(self):
        field_visits_list  = User_Inputs.site.field_visits
                
        peaks_label = Text_Line("Peak Verifications Section Preview", 11) 
        peaks_label.setSizePolicy(self.policy)
        self.layout.addRow(peaks_label)
        User_Inputs.record.create_peak_verifications_section(field_visits_list)
        peak_ver_html = User_Inputs.record.peak_verifications_section
        self.peak_verification_web_window = WebWindow(peak_ver_html, [1000, 400])
        self.peak_verification_web_window.setSizePolicy(self.policy)
    
        self.layout.addRow(self.peak_verification_web_window)
        update_button = self.peak_verification_web_window.return_update_button(self.update_peak_verification_section)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()
    
    def update_peak_verification_section(self):
        try:
            response = SynchronousAquariusAPISession.login()  # Capture the response
            if int(response) >= 400:  # Check for error status codes
                User_Inputs.critical_error_message(response.text)  # Display error message
                return False

            else:
                gh_ts_list = User_Inputs.site.gage_height_timeseries_list
                
                for ts in gh_ts_list:
                    ts.populate_datasets_for_records(User_Inputs.start_date, User_Inputs.end_date)

                field_visits_list  = User_Inputs.site.field_visits
                
                response = SynchronousAquariusAPISession.logout()  # Capture the response
                User_Inputs.record.create_peak_verifications_section(field_visits_list)
                new_html = User_Inputs.record.peak_verifications_section
                self.peak_verification_web_window.web_view.setHtml(new_html)
                
                if response >= 400:  # Check for error status codes
                    User_Inputs.critical_error_message(response.text)  # Display error message
                    return False
        
        except Exception as e:
            print(str(e.with_traceback))
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
                
        ts_peak_recorder_gh_label = Text_Line("Peak Recorder Section Preview", 11) 
        ts_peak_recorder_gh_label.setSizePolicy(self.policy)
        self.layout.addRow(ts_peak_recorder_gh_label)
        for box in self.peak_verification_input_combo_box_array:
            self.layout.addRow(box.field, box)
        User_Inputs.record.create_backup_data_section(gh_ts_list, self.peak_verification_input_combo_box_array)

        backup_html = User_Inputs.record.peak_recorder_stage_section
        self.peak_recorder_gh_web_window = WebWindow(backup_html, [800, 400])
        self.peak_recorder_gh_web_window.setSizePolicy(self.policy)
    
        self.layout.addRow(self.peak_recorder_gh_web_window)
        update_button = self.peak_recorder_gh_web_window.return_update_button(self.update_peak_recorder_gh_window)
        update_button.setSizePolicy(self.policy)
        self.layout.addRow(update_button)
        self.add_widget_spacer()    
        
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
                User_Inputs.record.peak_recorder_stage_section(gh_ts_list, self.peak_verification_input_combo_box_array)
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
        