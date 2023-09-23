from API_Session_V3 import SynchronousAquariusAPISession
from datetime import datetime
import re
import SiteV3
import Reading
import User_Inputs


class Field_Visit():
    EXTREME_MAX = "ExtremeMax"
    CSG = "Gage height, crest stage gage"
    
    def __init__(self, identifier: str, date: datetime.date, party: str, api_session: SynchronousAquariusAPISession = None):
        """
        Initialization method setting up all initial object attributes.
        
        Args:
            identifier(str): AQ's unique identifier for the field visit
            date(datetime.date): The date of the visit's occurrence
            party(str): The initials of the technicians involved in the visit
            api_session (SynchronousAquariusAPISession): The api_session, if provided, that connects to the NWIS family of web service
        """
        self.unique_id = identifier
        self.date = date
        self.party = party
        self.api_session = api_session or SynchronousAquariusAPISession()
        self.data_response = None
        self.checkbar_reading = None
        self.csg_inspection_code = ""
        self.csg_intake_code = ""
        self.csg_vent_code = ""
        self.has_stage_reading = False
        self.reset_amount = None
        self.reset_readings = []
        self.high_water_marks: list[SiteV3.Reading] = []
        self.dischage_measurements = []
        self.control_condition = ""
        self.levels_performed = False
        
    def retrieve_records_related_data(self,  gh_ts_list: list) -> None:
        """
        Helper method to retrieve all pertinent information for a field field to
        a surface water record. Must be provided the primary gage height timeseries id.
        This is needed for comparisons to the recorder values.
        
        Args:
            gh_ts_list(list[Timeseries.Generic_Timeseries]): List of all published gage height timeseries
            used to calculate published discharge values.        
        """
        self._retrieve_checkbar_reading()
        self._retrieve_high_water_mark_insp(gh_ts_list)
        self._check_for_resets()
        self._retrieve_discharge_info()
        if self.dischage_measurements != []:
            self._retrieve_control_insp()
        self.has_stage_reading = self._has_stage_readings()        
        
    def _retrieve_checkbar_reading(self) -> None:
        """
        Method to retrieve the checkbar reading for the visit if collected
        """
        if self.data_response == None:
            self.data_response = self.api_session.get_field_visit_data(self.unique_id)
        
        for inspection in self.data_response['InspectionActivity']['Inspections']:
            if inspection['InspectionType'] == "WireWeightGage":
                pattern = r"\d+\.\d+"
                match = re.search(pattern, inspection['Comments'])
                if match:
                    checkbar_reading = float(match.group())
                    cb_obj_reading = Reading.Reading("Elevation, Relative Datum", "Wire Weight Gage", "Calibration", str(self.date)[0:10], checkbar_reading)
                    self.checkbar_reading = cb_obj_reading
    
    @staticmethod
    def _has_time(json_reading_obj) -> bool:
        """
        Helper method to check whether a provided json entry for a reading has 
        a time. This is needed for CSG readings that cannot be correlated to a
        particular event.
        
        Args:
            json_reading_obj(json): The json entry from AQ featuring all the reading
            information.
        Return:
            has_datetime(bool): whether a provided reading response has a date and time
        """
        has_datetime = False
        for attr_key in json_reading_obj:
            if attr_key == 'Time':
                has_datetime = True
        return has_datetime
          
    def _retrieve_high_water_marks(self, gh_ts_list: list) -> None:
        """
        Helper method to retrieve the hw_readings from the AQ visit response.
        
        Args:
            gh_ts_list(list[Timeseries.Generic_Timeseries]): List of all published gage height timeseries
            check for discrepancy of any csg marks.
        """

        for reading in self.data_response['InspectionActivity']['Readings']:
            if reading['ReadingType'] == self.EXTREME_MAX and self._has_time(reading):
                reading_datetime = datetime.strptime(reading['Time'][0:19], "%Y-%m-%dT%H:%M:%S")
                hwm_reading_obj = Reading.Reading(reading['Parameter'], reading['MonitoringMethod'], reading['ReadingType'], reading_datetime, reading['Value']['Numeric'], sublocation = Field_Visit._return_reading_sublocation(reading))
                hwm_reading_obj.check_discrepancy(gh_ts_list)
                self.high_water_marks.append(hwm_reading_obj)

    @staticmethod
    def _return_reading_sublocation(reading_json: str):
        """
        Helper method to return the sublocation of the reading's json response
        from AQ if it exists. AQ will not return a sublocation index if one does
        not exist.
        """
        for param in reading_json:
            if param == "SubLocationIdentifier":
                return param["SubLocationIdentifier"]
        return ""

    def _retrieve_csg_intake_vent_insp(self) -> None:
        """
        Helper method to retrieve any inspections of the CSG pipe's conditions
        """
        for inspection in self.data_response['InspectionActivity']['Inspections']:
            if inspection['InspectionType'] == "CrestStageGage":
                INSPECTION_CODE_PATTERN = r"GageInspectedCode\s*=\s*([^\r\n]+)"
                INTAKE_HOLE_CONDITION_PATTERN = r"IntakeHoleConditionCode = (Open|Partially plugged|Plugged)"
                VENT_HOLE_CONDITION_PATTERN = r"VentHoleConditionCode = (Open|Partially plugged|Plugged)"
                
                inspection_code_match = re.search(INSPECTION_CODE_PATTERN, inspection['Comments'])
                intake_code_match = re.search(INTAKE_HOLE_CONDITION_PATTERN, inspection['Comments'])
                vent_code_match = re.search(VENT_HOLE_CONDITION_PATTERN, inspection['Comments'])
                
                if inspection_code_match:
                    self.csg_inspection_code = str(inspection_code_match.group(1).strip())
                    
                if intake_code_match:
                    self.csg_intake_code = str(intake_code_match.group(1).strip())
                    
                if vent_code_match:
                    self.csg_vent_code = str(vent_code_match.group(1).strip())
    
    def _retrieve_high_water_mark_insp(self, gh_ts_list: list):
        """
        Method to retrieve all of the crest stage gage information for a record.
        This includes any readings and inspection of the intake/vent.
        
        Args:
            gh_ts_list(list[Timeseries.Generic_Timeseries]): List of all published gage height timeseries
            check for discrepancy of any csg marks.
        """
        if self.data_response == None:
            self.data_response = self.api_session.get_field_visit_data(self.unique_id)

        self._retrieve_high_water_marks(gh_ts_list)
        self._retrieve_csg_intake_vent_insp() # Will ignore non-csg marks
        
    def _gather_reset_readings(self) -> None:
        for reading in self.data_response['InspectionActivity']['Readings']:
            if reading['ReadingType'] == 'ResetBefore' or reading['ReadingType'] == 'ResetAfter':
                self.reset_readings.append(Reading.Reading(reading['Parameter'], 
                                                          reading['MonitoringMethod'],
                                                          reading['ReadingType'],
                                                          datetime.strptime(reading['Time'][0:19], "%Y-%m-%dT%H:%M:%S"),
                                                          reading['Value']['Numeric']))
    
    def _determine_visit_reset_amount(self) -> None:
        """
        Method to determine how much the recorder was reset by during the visit
        if it was reset at all.
        """
        before_reset_reading = None
        after_reset_reading = None
        
        if len(self.reset_readings) == 2:
            for reading_obj in self.reset_readings:
                if reading_obj.reading_type =='ResetBefore':
                    before_reset_reading = reading_obj
                else:
                    after_reset_reading = reading_obj
            self.reset_amount = [round(float(after_reset_reading.value) - \
                                      float(before_reset_reading.value),2)]
        elif len(self.reset_readings) > 2:
            self.reset_amount = self._parse_multiple_resets()
    
    def _parse_multiple_resets(self):
        """
        Method to handle when there is not a simple before and after reset reading
        """
        self.reset_readings.sort(key=lambda x: x.datetime, reverse=False)
        resets = []

        for index, reading in enumerate(self.reset_readings):
            end_of_list = len(self.reset_readings) - 1 == index
            start_of_list = index == 0
            if (not end_of_list):
                next_reading = self.reset_readings[index+1]
                reading.next = next_reading
            else:
                reading.next = None
            
            if start_of_list:
                reading.previous = None
            else:
                previous_reading = self.reset_readings[index-1]
                reading.previous = previous_reading
            
            reading.checked = False

        
        for reading in self.reset_readings:
            if reading.reading_type == 'ResetBefore' and not reading.checked:
                next_read = reading.next
                
                while next_read.next != None and next_read.next.reading_type != 'ResetAfter':
                        next_read.checked = True
                        next_read = next_read.next
                
                amount = round(float(next_read.value) - \
                                      float(reading.value),2)
                reading.next.checked = True
                resets.append(amount)

            elif reading.reading_type == 'ResetAfter' and not reading.checked:
                User_Inputs.User_Inputs.warning_message("Error, after reset reading without before reading")

            reading.checked = True
        
        return resets

    
    def _check_for_resets(self) -> None:
        """
        Method to check for any resets and save the amount of reset.
        """
        if self.data_response == None:
            self.data_response = self.api_session.get_field_visit_data(self.unique_id)
        
        self._gather_reset_readings()                
        self._determine_visit_reset_amount()

    def _retrieve_discharge_info(self) -> None:
        """
        Method to retrieve all pertinent information related to the discharge
        measurements if any were made.
        """
        if self.data_response == None:
            self.data_response = self.api_session.get_field_visit_data(self.unique_id)
        
        if self.data_response['DischargeActivities'] != []:
            for qm in self.data_response['DischargeActivities']:
                qm_num = qm['DischargeSummary']['MeasurementId']
                qm_time = datetime.strptime(qm['DischargeSummary']['MeasurementTime'][0:19], "%Y-%m-%dT%H:%M:%S")
                method = qm['DischargeSummary']['DischargeMethod']
                mgh = qm['DischargeSummary']['MeanGageHeight']['Numeric']
                if len(qm['DischargeSummary']['DifferenceDuringVisit']) > 0:
                    diff_during_visit = qm['DischargeSummary']['DifferenceDuringVisit']['Numeric']
                else:
                    diff_during_visit = None
                discharge = qm['DischargeSummary']['Discharge']['Numeric']
                quality = qm['DischargeSummary']['MeasurementGrade']
                comment = qm['DischargeSummary']['Comments']
                qm_obj = Discharge_Measurement(qm_num, qm_time, method, mgh, diff_during_visit, discharge, quality, comment)
                self.dischage_measurements.append(qm_obj)
    
    @staticmethod
    def _check_for_distance_numeric(json_DistanceToGage_text) -> bool:
        """
        Method to check for whether a given snippet of json formatted text
        regarding the distance from the gage to the control actually contains
        a numeric distance entry from the visitor.
        
        Args:
            json_DistanceToGage_text(json): The json formatted text for the control distance
            inspection
        Return:
            numeric_present(bool): Whether the control inspection text contains a distance
        """
        numeric_present = False
        if len(json_DistanceToGage_text) == 2:
            numeric_present = True
        return numeric_present
    
    def _retrieve_control_insp(self) -> None:
        """
        Method to retrieve the control inspection information pertinent to a record.
        """
        if self.data_response == None:
            self.data_response = self.api_session.get_field_visit_data(self.unique_id)
        
        control_code = self.data_response['ControlConditionActivity']['ControlCode']
        control_condition = self.data_response['ControlConditionActivity']['ControlCondition']
        
        if control_condition == "DebrisLight":
            control_condition = "Light Debris"
        elif control_condition == "DebrisModerate":
            control_condition = "Moderate Debris"
        elif control_condition == "DebrisHeavy":
            control_condition = "Heavy Debris"
        
        has_numeric = Field_Visit._check_for_distance_numeric(self.data_response['ControlConditionActivity']['DistanceToGage'])
        distance = ""
        if has_numeric:
            distance = self.data_response['ControlConditionActivity']['DistanceToGage']['Numeric']
        
        self.control_condition = control_code + ", " + control_condition + ", " + str(distance) + "\' DS"
    
    def _has_stage_readings(self):
        if self.data_response == None:
            self.data_response = self.api_session.get_field_visit_data(self.unique_id)
        
        GAGE_HEIGHT = "Gage height"
        LAKE_NGVD29 = "Elevation, lake/res, NGVD29"
        LAKE_NAVD88 = "Elevation, lake/res, NAVD88"
        
        for reading in self.data_response['InspectionActivity']['Readings']:
            if reading['Parameter'] == GAGE_HEIGHT or reading['Parameter'] == LAKE_NGVD29 or reading['Parameter'] == LAKE_NAVD88:
                return True
        
        return False
    
class Discharge_Measurement():
    """
    Class object representing a single discharge measurement
    """
    def __init__(self, qm_num: int, qm_time: datetime, method: str, mgh: float, diff_during_visit: float, discharge: float, quality: str, comment: str = ""):
        """
        Initialization method.
        
        Args:
            qm_num(int): The discharge measurement's number
            qm_time(datetime.datetime): Time at which the measurement was collected
            method(str): The method used to collect the discharge measurement 
            mgh(float): Mean gage height
            diff_during_visit(float): The difference in gage height during the measurement
            discharge(float): Streamflow in cubic feet per second (cfs)
            quality(str): The visitor's assigned qualitative quality rating
            comment(str): The visitor's commentary on their discharge measurement
        """
        self.qm_num = qm_num
        self.qm_time = qm_time
        self.method = method
        self.mgh = mgh
        self.diff_during_visit = diff_during_visit
        self.discharge = discharge
        self.quality = quality
        self.difference_from_base_rating = None
        self.rating_num_compared = ""
        self.comment = comment
             