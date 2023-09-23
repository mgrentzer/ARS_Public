from API_Session_V3 import SynchronousAquariusAPISession
from datetime import datetime

class Rating_Model():
    """
    Class object represent the discharge rating computation model. This is 
    functionally a container for the rating curves.
    """
    def __init__(self, rating_model_id: str, api_session: SynchronousAquariusAPISession = None) -> None:
        """
        Initialization method
        
        Args:
            rating_model_id(str): The rating model's unique ID as assigned by AQ
            api_session(SynchronousAquariusAPISession): The api_session, if provided, that connects to the NWIS family of web services
        """
        self.rating_model_id = rating_model_id
        self.api_session = api_session or SynchronousAquariusAPISession()
        self.ratings_list = []
        self.rating_model_response = None
    
    def retrieve_info_for_record(self, record_start_date: datetime, record_end_date: datetime) -> None:
        """
        Helper method to retrieve all pertinent information relevant to a record.
        
        Args:
            record_start_date(datetime.datetime): Date of when the record begins
            record_end_date(datetime.datetime): Date of when the record ends
        """
        self.rating_model_response = self.api_session.get_discharge_rating_model_info(self.rating_model_id, record_start_date, record_end_date)
        self._populate_ratings_list()
        
    def _populate_ratings_list(self) -> None:
        """
        Method to populat the list of rating curves including all of their
        information pertinent to a surface water record.
        """
        for rating_curve in self.rating_model_response['RatingCurves']:
            start_datetime = datetime.strptime(rating_curve["PeriodsOfApplicability"][0]["StartTime"][0:19], "%Y-%m-%dT%H:%M:%S")
            last_rating_applicability_period_index = len(rating_curve["PeriodsOfApplicability"])-1 # Debug: Server does not merge same periods
            end_datetime = datetime.strptime(rating_curve["PeriodsOfApplicability"][last_rating_applicability_period_index]["EndTime"][0:19], "%Y-%m-%dT%H:%M:%S")
            rating_obj = Rating(rating_curve["Id"], self.rating_model_id, start_datetime, end_datetime, rating_curve["Remarks"], self.api_session)
            rating_obj.populate_shift_list(self.rating_model_response)
            self.ratings_list.append(rating_obj)

    def return_rating_curve_id_for_datetime(self, datetime):
        """
        Method to return the rating ID of the rating that was in effect for
        a provided datetime. Used to filter for ratings that are used
        during the rating period.

        Args:
            datetime(datetime.datetime): Date and time being inspect for effective rating ID
        """
        rating_id = ""
        for rating in self.ratings_list:
            after = datetime >= rating.start_datetime
            before = datetime <= rating.end_datetime
            if datetime >= rating.start_datetime and datetime <= rating.end_datetime:
                rating_id = rating.rating_id
        return rating_id

class Rating():
    """
    A class object representing a single rating curve.
    """
    def __init__(self, rating_id: str, rating_model_id: str, start_datetime, end_datetime, comment: str = None, api_session: SynchronousAquariusAPISession = None):
        """
        Initialization method
        
        Args:
            rating_id(str): The unique ID/name provided by a records worker for the rating curve
            rating_model_id(str): The unique ID assigned by AQ to the rating model for which the rating belongs to. This is needed
            for retrieving rating curve information if was not already retrieved.
            comment(str): Comments provided by the rating drafter documenting the rating
        """
        self.rating_id = rating_id
        self.rating_model_id = rating_model_id
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.shift_curve_list = []
        self.api_session = api_session or SynchronousAquariusAPISession()
    
    def _append_shift_curves_to_list_from_json(self, json_shifts_list) -> None:
        """
        Helper method to process the json list of shift curves, create Shift_Curve objects, and append them to shift_curve
        list for the rating_curve object. Ensures that the shift's end time is the next shift's beginning time if not
        assisgned by the analyzer.
        
        Args:
            json_shifts_list(json): JSON formatted response string containing a list of shift curves
        """
        for index, shift in enumerate(json_shifts_list):
            
            shift_start_datetime = datetime.strptime(shift['PeriodOfApplicability']['StartTime'][0:19], "%Y-%m-%dT%H:%M:%S")
            shift_end_datetime = datetime.strptime(shift['PeriodOfApplicability']['EndTime'][0:19], "%Y-%m-%dT%H:%M:%S")
            shift_points_list = []
            for shift_point in shift["ShiftPoints"]:
                shift_points_list.append([float(shift_point["InputValue"]), float(shift_point["Shift"])])
            shift_comment = shift['PeriodOfApplicability']["Remarks"]
            shift_curve_obj = Shift_Curve(shift_start_datetime, shift_end_datetime, shift_points_list, shift_comment)
            shift_curve_obj.gather_records_info()
            
            if index > 0:
                shift_curve_obj.previous = self.shift_curve_list[index-1]
                self.shift_curve_list[index-1].previous = shift_curve_obj

            self.shift_curve_list.append(shift_curve_obj)
            
    
    def populate_shift_list(self, rating_model_response_info = None) -> None:
        """
        Method to populated the rating's list of shift curves and all their information pertinent to a surface water reocord.
        
        Args:
            rating_model_response_info(json): The AQ response containing info on the discharge rating model.
        """
        if rating_model_response_info == None:
            self.rating_model_repsonse = self.api_session.get_discharge_rating_model_info(self.rating_model_id)          
        
        shifts_list = []
        for rating_curve in rating_model_response_info['RatingCurves']:
            if rating_curve["Id"] == self.rating_id:
                shifts_list = rating_curve["Shifts"]
                
        self._append_shift_curves_to_list_from_json(shifts_list)

class Shift_Curve():
    """
    Object class representing a single rating shift curve.
    """
    def __init__(self, start_datetime: datetime, end_datetime: datetime, shift_point_list, comment: str = None) -> None:
        """
        Initialization method
        
        Args:
            start_datetime(datetime.datetime): Starting datetime of the shift
            end_datetime(datetime.datetime): Ending datetime of the shift
            starting_shift_point_list([float, float]): List of the starting shift input points
            comment(str): The analyzer's comments regarding the shift
        """
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.shift_point_list = shift_point_list
        self.start_type = ""
        self.shape = ""
        self.comment = comment
        self.reported_magnitude = ""
        self.next = None
        self.previous = None
        self.shift_gh_change = None
        self.long_reported_values = False
    
    def gather_records_info(self):
        self.shift_gh_change = self.determine_if_input_pt_gh_changed()
        self.determine_shift_type()
        self.determine_reported_magnitude_for_table()
    
    def determine_shift_type(self):
        
        first_input_point_magnitude = round(self.shift_point_list[0][1], 2)
        
        if(len(self.shift_point_list) == 1):
            if(first_input_point_magnitude == 0):
                self.shape = "Null-Shift"
            else:
                self.shape = "Full-Rating Shift"
                
        elif(len(self.shift_point_list) == 2):
            second_input_point_magnitude = round(self.shift_point_list[1][1], 2)
            if(first_input_point_magnitude == 0 and second_input_point_magnitude == 0):
                self.shape = "Null-Shift"
            elif(first_input_point_magnitude != 0 and second_input_point_magnitude == 0):
                self.shape = "Half-House"
            elif(first_input_point_magnitude == 0 and second_input_point_magnitude != 0):
                self.shape = "Reverse Half-House"
            else:
                self.shape = "Full-Rating Shift"
        
        else:
            second_input_point_magnitude = round(self.shift_point_list[1][1], 2)
            third_input_point_magnitude = round(self.shift_point_list[2][1], 2)
            if(first_input_point_magnitude == 0 and second_input_point_magnitude == 0 and third_input_point_magnitude == 0):
                self.shape = "Null-Shift"
            elif(first_input_point_magnitude == 0 and second_input_point_magnitude == 0 and third_input_point_magnitude != 0):
                self.shape = "Reverse Half-House"  
            elif(first_input_point_magnitude == 0 and second_input_point_magnitude != 0 and third_input_point_magnitude == 0):
                if(first_input_point_magnitude == third_input_point_magnitude):
                    self.shape = "Trellis"
                elif(first_input_point_magnitude != third_input_point_magnitude):
                    both_positive = first_input_point_magnitude > 0 and third_input_point_magnitude > 0
                    both_negative = first_input_point_magnitude < 0 and third_input_point_magnitude < 0
                    if(both_positive or both_negative):
                        self.shape = "Asymmetric Trellis"
                    else:
                        self.shape = "NON-STANDARD"
            elif(first_input_point_magnitude == 0 and second_input_point_magnitude != 0 and third_input_point_magnitude != 0):
                if(second_input_point_magnitude == third_input_point_magnitude):
                    self.shape = "Reverse Half-House"
                else:
                    self.shape = "Crooked Reverse Half-House"
            elif(first_input_point_magnitude != 0 and second_input_point_magnitude == 0 and third_input_point_magnitude == 0):
                self.shape = "Half-House"  
            elif(first_input_point_magnitude != 0 and second_input_point_magnitude == 0 and third_input_point_magnitude != 0):
                self.shape = "NON-STANDARD"   
            elif(first_input_point_magnitude != 0 and second_input_point_magnitude != 0 and third_input_point_magnitude == 0):
                if(first_input_point_magnitude == second_input_point_magnitude):
                    self.shape = "Half-House"
                else:
                    self.shape = "Crooked Half-House"
            elif(first_input_point_magnitude != 0 and second_input_point_magnitude != 0 and third_input_point_magnitude != 0):
                self.shape = "Full-Rating Shift"
    
    @staticmethod
    def _input_pt_list_to_string(shift_input_point_list):
        tuple_list = ""
        if len(shift_input_point_list) == 0:
            tuple_list = "None"
        else:
            for index, shift_tuple in enumerate(shift_input_point_list):
                tuple_list = tuple_list + f"({shift_tuple[0]:.2f}\', {shift_tuple[1]:.2f}\')"
                if index + 1 < len(shift_input_point_list):
                    tuple_list = tuple_list + ", "

        return tuple_list
    
    def determine_reported_magnitude_for_table(self):
        if self.shift_gh_change == None:
            self.shift_gh_change = self.determine_if_input_pt_gh_changed()
            
        if(self.shift_gh_change):
            self.reported_magnitude = Shift_Curve._input_pt_list_to_string(self.shift_point_list)
            self.long_reported_values = True
        elif(self.shape == "Null-Shift"):
            self.reported_magnitude = "0.00\'"
        elif(self.shape == "Half-House"):
            first_input_point_magnitude = round(self.shift_point_list[0][1], 2)
            self.reported_magnitude = f"{first_input_point_magnitude:.2f}\'"
        else:
            self.reported_magnitude = Shift_Curve._input_pt_list_to_string(self.shift_point_list)
            self.long_reported_values = True

    def determine_if_input_pt_gh_changed(self):
        if self.previous != None:
            for gh_previous_shift_input_pt, gh_current_shift_input_pt in zip(self.previous.shift_point_list, self.shift_point_list):
                if(gh_previous_shift_input_pt[0] != gh_current_shift_input_pt[0]):
                    return True
        
        return False
        