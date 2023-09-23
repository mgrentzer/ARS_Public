from API_Session_V3 import SynchronousAquariusAPISession
from PyQt5.QtWidgets import QScrollArea, QWidget, QLabel, QLineEdit, QFormLayout
from PyQt5 import QtCore
from Text_Line import Text_Line
from User_Inputs import User_Inputs
from WebWindow import WebWindow
from ComboBox import ComboBox
from Quality_Section import Quality_Section
from Generic_Tab import Generic_Tab

class QRatingTab(Generic_Tab):
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
        self.setup_section("Rating Description Section Preview",
                           User_Inputs.site._gather_ratings_description,
                           lambda: User_Inputs.record.create_rating_description(User_Inputs.site.ratings_description),
                           "rating_section")
        
        self.setup_section("Measurements Section Preview",
                           QRatingTab._update_measurement_related_data,
                           lambda: User_Inputs.record.create_qm_section(User_Inputs.site.field_visits),
                           "qm_section",
                           1000,
                           600)
        
        self.setup_section("Shift Table Section Preview",
                           lambda: User_Inputs.site._populate_rating_models(User_Inputs.start_date, User_Inputs.end_date),
                           lambda: User_Inputs.record.create_shift_curves_section(User_Inputs.site.rating_model.ratings_list),
                           "shift_section",
                           1000)
    
    @staticmethod
    def _update_measurement_related_data():
        User_Inputs.site._gather_field_visits(User_Inputs.start_date, User_Inputs.end_date),
        User_Inputs.site._populate_rating_models(User_Inputs.start_date, User_Inputs.end_date)
        User_Inputs.site._backcheck_qm_difference()
        
        

    

