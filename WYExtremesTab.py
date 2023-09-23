from API_Session_V3 import SynchronousAquariusAPISession
from PyQt5.QtWidgets import QScrollArea, QWidget, QLabel, QLineEdit, QFormLayout
from PyQt5 import QtCore
from Text_Line import Text_Line
from User_Inputs import User_Inputs
from WebWindow import WebWindow
from ComboBox import ComboBox
from Quality_Section import Quality_Section
from Generic_Tab import Generic_Tab


class WYTab(Generic_Tab):
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
    
    @staticmethod
    def _update_water_year_datasets():
        for gh_ts in User_Inputs.site.gage_height_timeseries_list:
            gh_ts._gather_water_year_dataset_list(User_Inputs.start_date, User_Inputs.end_date)
        
        for q_ts in User_Inputs.site.discharge_timeseries_list:
            q_ts._gather_water_year_dataset_list(User_Inputs.start_date, User_Inputs.end_date)

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
        
        self.layout.removeRow(0)

        self.setup_section("Water Year Extremes Table Preview", 
                            WYTab._update_water_year_datasets,
                            lambda: User_Inputs.record._create_wy_extremes_table_section(User_Inputs.site),
                            "water_year_section")


        

    

