from API_Session_V3 import SynchronousAquariusAPISession
from datetime import datetime


class Dataset():
    """
    Class representing a timeseries dataset including all information
    associated with and found through Aquarius' Data Review Tool
    
    Requires: start is some date before end date, ts_unique_id exists within AQ
    
    Args:
        GH_TS_unique_id(str): The Aquarius assigned alphanumeric ID for the timeseries
        dataset_start_date(datetime.date): Date of when the dataset begins
        dataset_end_date(datetime.date): Date of when the dataset begins
        api_session(SynchronousAquariusAPISession): The api_session, if provided, that connects to the NWIS family of web services
    """
    
    EMPTY ="EMPTY"
    
    def __init__(self, ts_unique_id : str, dataset_start_date: datetime.date, dataset_end_date: datetime.date, api_session: SynchronousAquariusAPISession = None) -> None:
        """
        Initialize the dataset object with default null and empty values
        """
        
        self.data: list[Data_Point] = []
        self.max_point = None
        self.min_point = None
        self.general_corrections: list[Correction] = []
        self.multipoint_corrections: list[Multi_Point_Correction] = []
        self.qualifiers: list[Qualifier] = []
        self.gap_tolerances: list[Gap_Tolerance] = []
        self.gaps: list[Gap] = []
        
        self.ts_data_response = None
        # Full coverage entails having first values before start datetime and after end datetime with gap markers
        self.ts_data_response_full_coverage = None
        self.dataset_corrections_response = None
        
        self.ts_unique_id = ts_unique_id
        self.dataset_start_date = dataset_start_date
        self.dataset_end_date = dataset_end_date
        self.api_session = api_session or SynchronousAquariusAPISession()
    
    def gather_data_for_records(self) -> None:
        """
        Conveniency method to populate the dataset object with all information pertinent to
        a record.
        """
        self._gather_data()
        self._assess_qualifiers()
        self._assess_general_corrections()
        self._gather_usgs_multipoint_corrections()
        self._assess_gaps()
        self._assess_max()
        self._assess_min()
    
    
    def _gather_data(self) -> None:
        """
        Method to gather timeseries unit value data from AQ (if not already done),
        convert to a data_point object with datetime and value, and finally append
        to a list of data_point objects.
        """
        if self.ts_data_response == None:
            self.ts_data_response = self.api_session.get_timeseries_data(self.ts_unique_id, self.dataset_start_date, self.dataset_end_date, False, False)
        
        for index, point in enumerate(self.ts_data_response['Points']):
            pt_time = datetime.strptime(point['Timestamp'][0:19], "%Y-%m-%dT%H:%M:%S")
            
            value = point['Value']['Numeric']
            if index > 0:
                self.data.append(Data_Point(pt_time, round(float(value), 2), None))
                self.data[index-1].next = self.data[index]
            else:
                self.data.append(Data_Point(pt_time, round(float(value), 2), None))
        
    def _assess_qualifiers(self) -> None:
        """
        Method to assess whether the a timeseries dataset has qualifiers, converts
        qualifier to a Qualifier object, and then appends them to a list of 
        Qualifier objects. The dataset being evaluated must have full coverage
        (contain starting at start of period or before and v/v for end of period).
        """
        if self.ts_data_response_full_coverage == None:
            self.ts_data_response_full_coverage = self.api_session.get_timeseries_data(self.ts_unique_id, self.dataset_start_date, self.dataset_end_date, True, True)
        
        for qualifier in self.ts_data_response_full_coverage['Qualifiers']:
            start = datetime.strptime(qualifier['StartTime'][0:19], "%Y-%m-%dT%H:%M:%S")
            end = datetime.strptime(qualifier['EndTime'][0:19], "%Y-%m-%dT%H:%M:%S")
            identifier = qualifier['Identifier']
            self.qualifiers.append(Qualifier(start, end, identifier))  
    
    def _assess_general_corrections(self) -> None:
        """
        Method to gather and populate a list of generic timeseries corrections/
        edits. These do not include Multi-Point corrections which are seperate
        and more nuanced.
        """
        if self.dataset_corrections_response == None:
            self.dataset_corrections_response = self.api_session.get_gh_corrections_list(self.ts_unique_id, self.dataset_start_date, self.dataset_end_date)
        
        for correction in self.dataset_corrections_response['Corrections']:
            if(correction['Type'] != 'USGSMultiPoint' and correction['Type'] != 'ThresholdSuppression'):
                start = datetime.strptime(correction['StartTime'][0:19], "%Y-%m-%dT%H:%M:%S")
                end = datetime.strptime(correction['EndTime'][0:19], "%Y-%m-%dT%H:%M:%S")
                processing_order = correction['ProcessingOrder']
                comment = correction['Comment']
                self.general_corrections.append(Correction(correction['Type'], start, end, processing_order, comment))
    
    @staticmethod
    def _has_end_shift_points(correction_shift_input_pt_json) -> bool:
        """
        Helper method to check whether a multi-point correction has an end
        set of shift input points (correction proration).
        
        Args:
            correction_entry(json): A json entry containing the shift input points
            of a multi-point correction.
        """
        for key in correction_shift_input_pt_json:
            if key == 'EndShiftPoints':
                return True
                
        return False
    
    @staticmethod
    def _gather_start_shift_input_points(correction_entry_json):
        shift_input_point_list = []
        for shift_input_point in correction_entry_json['Parameters']['StartShiftPoints']:
                    shift_gh = shift_input_point["Value"]
                    shift_magnitude = shift_input_point["Offset"]
                    shift_input_point_list.append([float(shift_gh), float(shift_magnitude)])
        
        return shift_input_point_list
    
    @staticmethod
    def _gather_end_shift_input_points(correction_entry_json):
        shift_input_point_list = []
        for shift_input_point in correction_entry_json['Parameters']['EndShiftPoints']:
                    shift_gh = shift_input_point["Value"]
                    shift_magnitude = shift_input_point["Offset"]
                    shift_input_point_list.append([float(shift_gh), float(shift_magnitude)])
        
        return shift_input_point_list
    
    def _gather_usgs_multipoint_corrections(self) -> None:
        """
        Method to populate a list of Multi-Point corrections from a provided 
        AQ response regarding a timeseries period.
        """
        if self.dataset_corrections_response == None:
            self.dataset_corrections_response = self.api_session.get_gh_corrections_list(self.ts_unique_id, self.dataset_start_date, self.dataset_end_date)
           
        for correction in self.dataset_corrections_response['Corrections']:
            if(correction['Type'] == 'USGSMultiPoint'):
                correction_start_datetime = datetime.strptime(correction['StartTime'][0:19], "%Y-%m-%dT%H:%M:%S")
                correction_end_datetime = datetime.strptime(correction['EndTime'][0:19],"%Y-%m-%dT%H:%M:%S")
                start_shifts = Dataset._gather_start_shift_input_points(correction)
                end_shifts = []
                
                if self._has_end_shift_points(correction["Parameters"]):
                    end_shifts = Dataset._gather_end_shift_input_points(correction)
                    
                processing_order = correction['Parameters']['UsgsType']
                comment = correction['Comment']
                self.multipoint_corrections.append(Multi_Point_Correction(correction_start_datetime, correction_end_datetime, start_shifts, end_shifts, processing_order, comment))
    
    def _assess_gaps(self) -> None:
        """
        Method to assess whether there are in gaps in a given timeseries, convert
        them into Gap objects, and append them to a list of Gap objects.
        """
        if self.ts_data_response_full_coverage == None:
            self.ts_data_response_full_coverage = self.api_session.get_timeseries_data(self.ts_unique_id, self.dataset_start_date, self.dataset_end_date, True, True)
        
        if self.ts_data_response_full_coverage['NumPoints'] == 0:
            period_duration = self.dataset_end_date-self.dataset_start_date
            self.gaps.append(Gap(self.dataset_start_date, self.dataset_end_date, period_duration))
        
        for index, point in enumerate(self.ts_data_response_full_coverage['Points']):
            if len(point['Value']) > 0:
                value = point['Value']['Numeric']
                if value == Dataset.EMPTY:
                    previous_uv_time = datetime.strptime(self.ts_data_response_full_coverage['Points'][index-1]['Timestamp'][0:16], "%Y-%m-%dT%H:%M")
                    next_uv_time = datetime.strptime(self.ts_data_response_full_coverage['Points'][index+1]['Timestamp'][0:16], "%Y-%m-%dT%H:%M")
                    gap_duration = next_uv_time-previous_uv_time
                    self.gaps.append(Gap(previous_uv_time, next_uv_time, gap_duration))
            elif len(point['Value']) == 0 and index != len(self.ts_data_response_full_coverage['Points'])-1:
                curr_uv_time = datetime.strptime(self.ts_data_response_full_coverage['Points'][index-1]['Timestamp'][0:16], "%Y-%m-%dT%H:%M")
                next_uv_time = datetime.strptime(self.ts_data_response_full_coverage['Points'][index+1]['Timestamp'][0:16], "%Y-%m-%dT%H:%M")
                gap_duration = next_uv_time - curr_uv_time
                self.gaps.append(Gap(curr_uv_time, next_uv_time, gap_duration))
                
    def _check_if_estimated(self, data_point_to_check) -> bool:
        estimated = False
        for qualifier in self.qualifiers:
            if qualifier.identifier == "ESTIMATED":
                if data_point_to_check.datetime >= qualifier.start_datetime and data_point_to_check.datetime <= qualifier.end_datetime:
                    estimated = False
        return estimated
    
    def _assess_min(self) -> None:
        """
        Method to determine and assign the minimum unit value of the dataset.
        """
        if len(self.data) > 0:
            self.data.sort(key=lambda x: x.value, reverse = False)
            self.min_point = self.data[0]
            self.min_point.estimated = self._check_if_estimated(self.min_point)
            if self.min_point.value == self.data[1].value:
                self.min_point.unique = False
    
    def _assess_max(self) -> None:
        """
        Method to determine and assign the maximum unit value of the dataset.
        """
        if len(self.data) > 0:
            self.data.sort(key=lambda x: x.value, reverse = True)
            first_valid_point_index = 0

            while(self.data[first_valid_point_index].value == Dataset.EMPTY):
                first_valid_point_index = first_valid_point_index + 1
            
            self.max_point = self.data[first_valid_point_index]
            self.max_point.estimated = self._check_if_estimated(self.max_point)
            if first_valid_point_index != len(self.data) - 1:
                if self.max_point.value == self.data[first_valid_point_index + 1].value:
                    self.max_point.unique = False
            self.max_point.estimated = self._check_if_estimated(self.max_point)

class Correction():
    """
    Class object representing a general correction (not a multi-point) to the timeseries record
    
    Args:
            correction_type(str): The type of correction (deletion, note, copypaste, etc.)
            start_datetime(datetime.datetime): Starting datetime of the correction
            end_datetime(datetime.datetime): Ending datetime of the correction
            processing_order(str): The order at which the correction is handled relative to other corrections
            desription(str): Any remarks provided by the analyzer regarding the correction
    """
    def __init__(self, correction_type: str, start_datetime: datetime, end_datetime: datetime, processing_order: str, description: str = "") -> None:
        self.correction_type = correction_type
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.processing_order = processing_order
        self.description = description

class Multi_Point_Correction():
    """
    Class object representing a multip-point correction to the timeseries record
    
    Args:
            start_datetime(datetime.datetime): Starting datetime of the multi-point correction
            end_datetime(datetime.datetime): Ending datetime of the multi-point correction
            start_shifts([(float, float)]): A list of correction input points in case there are prorations with respect to gage height
            end_shifts([(float, float)]): A list of correction input points in case there are prorations with respect to gage height
            processing_order(str): The order at which the correction is handled relative to other corrections
            desription(str): Any remarks provided by the analyzer regarding the correction
    """
    def __init__(self, start_datetime: datetime, end_datetime: datetime, start_shifts, end_shifts, processing_order: str, description: str = "") -> None:
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.start_shifts = start_shifts
        self.end_shifts = end_shifts
        self.processing_order = processing_order
        self.description = description
        

class Qualifier():
    """
    Class object representing a qualifier to the timeseries record
    
    Args:
            start_datetime(datetime.datetime): Starting datetime of the qualifier
            end_datetime(datetime.datetime): Ending datetime of the qualifier
            identifier(str): The type of qualifier (ICE, ZEROFLOW, etc.)
    """
    def __init__(self, start_datetime: datetime, end_datetime: datetime, identifier: str):
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.identifier = identifier

class Gap_Tolerance():
    """
    Class object representing a period of defined gap tolerance. Gaps less than the tolerance amount are automatically
    interpolated by Aquarius
    
    Args:
            start_datetime(datetime.datetime): Starting datetime of the gap tolerance period
            end_datetime(datetime.datetime): Ending datetime of the gap tolerance period
            tolerance_duration(int): The threshold for automatic gap interpolation
    """
    def __init__(self, start_datetime: datetime, end_datetime: datetime, tolerance_duration: int):
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.tolerance_duration = tolerance_duration
    
class Gap():
    """
    Class object representing a gap in the timeseries record
    
    Args:
            start_datetime(datetime.datetime): Starting datetime of the gap
            end_datetime(datetime.datetime): Ending datetime of the gap
            length(int): The number of minutes for which the gap represents
    """
    def __init__(self, start_datetime: datetime, end_datetime: datetime, length: int):
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.length = length

class Data_Point():
    """
    Class object representing a single data point/unit value
    
    Args:
            datetime(datetime.datetime): Datetime of the unit value's occurence
            value(float): The unit value's value
            next_pt(Dataset.Data_Point): The sequential Data_Point in the timeseries, needed for discrepancy computations
    """
    def __init__(self, datetime: datetime, value: float, next_pt):
        self.datetime = datetime
        self.value = value
        self.next = next_pt
        self.estimated = False
        self.unique = True
