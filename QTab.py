from PyQt5.QtWidgets import QTextEdit
from PyQt5 import QtCore
from User_Inputs import User_Inputs
from Quality_Section import Quality_Section
from Generic_Tab import Generic_Tab

class QTab(Generic_Tab):
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
        self.q_quality_sections = []
    
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
        
        self.setup_and_add_all_sections()

    def setup_and_add_all_sections(self):
        self.layout.removeRow(0)
        self.q_quality_section = Quality_Section("Discharge Quality Rating",
                                            User_Inputs.site.discharge_timeseries_list, 
                                            User_Inputs.q_tables_list,
                                            self.layout,
                                            self.policy)
        
        self.q_quality_section.setup_quality_tables()

        self.setup_section("Discharge Gaps Section Preview",
                                self._update_q_ts,
                                lambda: User_Inputs.record.create_q_data_gaps_section(User_Inputs.site.discharge_timeseries_list[0].record_dataset.gaps),
                                "q_data_gaps_section")

        self.setup_section("Discharge Estimates Section Preview",
                           self._update_q_ts,
                           lambda: User_Inputs.record.create_estimate_section(User_Inputs.site.discharge_timeseries_list[0].record_dataset.general_corrections),
                           "estimates_section")
        
        self.setup_section("Backwater Section Preview",
                           self._update_q_ts,
                           lambda: User_Inputs.record.create_backwater_section(User_Inputs.site.discharge_timeseries_list[0].record_dataset.qualifiers),
                           "backwater_section")

        self.setup_hydro_comp_section()

        self.setup_section("Peak Streamflow Section Preview",
                           self._update_q_ts,
                           lambda: User_Inputs.record.create_peak_record_discharge_table(User_Inputs.site.discharge_timeseries_list[0].record_dataset),
                           "peak_recorder_streamflow_section")

    
    def setup_hydro_comp_section(self):
        """
        Method to add the special notes section to the gage height tab.
        """
        self._add_label("Hydrographic Comparison Section")
        self.hydro_comp_text_box = QTextEdit()
        self.hydro_comp_text_box.setSizePolicy(self.policy)
        self.hydro_comp_text_box.setFixedSize(800, 400)
        self.hydro_comp_text_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.hydro_comp_text_box.textChanged.connect(self.update_user_inputs)

        if User_Inputs.successfulSubmissionCnt > 1:
            self.hydro_comp_text_box.setText(User_Inputs.hydro_comp)

        self.layout.addRow(self.hydro_comp_text_box)
        self.add_widget_spacer()
    
    def update_user_inputs(self):
        """
        Instance method to update the shared User Inputs object class whenever the
        user makes changes to the text and calandar/date fields. If there was a 
        successful data pull from AQ, a warning message will alert the user that
        they must click the resubmit button to update their end product.
        """
        
        User_Inputs.hydro_comp = self.hydro_comp_text_box.toPlainText()
        

    

