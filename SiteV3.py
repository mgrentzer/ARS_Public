from API_Session_V3 import SynchronousAquariusAPISession, SynchronousSIMsAPISession
from datetime import datetime, timedelta
import Field_Visit
import Timeseries
import Rating
from Sensor import Sensor
        
class Site():
    
    """
    Class representing a USGS site with a stage recorder.

    A site is characterized by having a descriptive name, unique 8 or 11 digit ID number,
    and a unique alphanumeric ID associated with it within Aquarius.
    """
    
    def __init__(self, site_no: str, api_session: SynchronousAquariusAPISession = None) -> None:
        """
        Initialize the Site object.

        Args:
            site_no (str): The ID number of the site.
            api_session(SynchronousAquariusAPISession): The api_session, if provided, that connects to the NWIS family of web services
        """
        self.site_no = site_no
        self.site_name = ""
        self.unique_id = ""
        self.gage_height_timeseries_list: list[Timeseries.Generic_Timeseries] = []
        self.discharge_timeseries_list: list[Timeseries.Generic_Timeseries] = []
        self.rating_model = None
        self.levels_description = ""
        self.ratings_description = ""
        self.api_session = api_session or SynchronousAquariusAPISession() # optional dependency injection
        self.field_visits = []
        self._gather_site_info()
        self.rating_info = ""
        self.sensors = []
    
    def gather_records_info_from_dates(self, record_start_date, record_end_date):
        """
        Method to gather information relevent to a record based on provided
        dates.
        
        Args:
            record_start_date(datetime.date): Date of when the record begins
            record_end_date(datetime.date): Date of when the record ends
        """
        self._gather_GH_TS_list(record_start_date, record_end_date)
        self._gather_sensors_list(self.site_no)
        self._gather_levels_description()
        self._gather_field_visits(record_start_date, record_end_date)
        self._gather_Q_TS_list(record_start_date, record_end_date)
        if len(self.discharge_timeseries_list) > 0:
            self._gather_ratings_description()
            self._populate_rating_models(record_start_date, record_end_date)
            self._backcheck_qm_difference()
        
    def _gather_site_info(self):
        """
        Gather the site's English name and unique ID
        """
        site_info_tuple = SynchronousAquariusAPISession.get_site_info(self.site_no)
        self.site_name = site_info_tuple[0]
        self.unique_id = site_info_tuple[1]
        
    @staticmethod
    def _populate_Aquarius_stage_timeseries_reponse(site_no: str):
        """
        Helper method for retrieval of the AQ response list handling various
        different paramter representations of stage (relative datum, NGVD88, etc.)
        
        Args:
            site_no (str): The ID number of the site.
        """
        
        GAGE_HEIGHT = "Gage height"
        LAKE_NGVD29 = "Elevation, lake/res, NGVD29"
        LAKE_NAVD88 = "Elevation, lake/res, NAVD88"
        
        list_of_AQ_TS_info = SynchronousAquariusAPISession.get_timeseries_list(site_no, GAGE_HEIGHT)
        
        if list_of_AQ_TS_info == []:
            list_of_AQ_TS_info = SynchronousAquariusAPISession.get_timeseries_list(site_no, LAKE_NGVD29)
            
        elif list_of_AQ_TS_info == []:
            list_of_AQ_TS_info = SynchronousAquariusAPISession.get_timeseries_list(site_no, LAKE_NAVD88)
        
        return list_of_AQ_TS_info    

    def _gather_GH_TS_list(self, record_start_date, record_end_date):
            """
            Gather the site's gage height timeseries unique IDs, create their object representations, append to
            a list of said objects.
            
            Args:
                record_start_date(datetime.date): Date of when the record begins
                record_end_date(datetime.date): Date of when the record ends
            """
            
            list_of_AQ_TS_info = Site._populate_Aquarius_stage_timeseries_reponse(self.site_no)
            
            for timeseries in list_of_AQ_TS_info:
                identifier = timeseries['Identifier']
                unique_id = timeseries['UniqueId']
                sublocation = timeseries['SubLocationIdentifier']
                gs_ts_list_element = Timeseries.Generic_Timeseries(identifier, unique_id, sublocation)
                gs_ts_list_element.populate_datasets_for_records(record_start_date, record_end_date)
                
                self.gage_height_timeseries_list.append(gs_ts_list_element)
    
    
    def _gather_Q_TS_list(self, record_start_date, record_end_date):
            """
            Gather the site's discharge timeseries unique IDs, create their object representations, append to
            a list of said objects.
            
            Args:
                record_start_date(datetime.date): Date of when the record begins
                record_end_date(datetime.date): Date of when the record ends
            """
            
            DISCHARGE = "Discharge"
            list_of_AQ_TS_info = SynchronousAquariusAPISession.get_timeseries_list(self.site_no, DISCHARGE)
            
            for timeseries in list_of_AQ_TS_info:
                identifier = timeseries['Identifier']
                unique_id = timeseries['UniqueId']
                sublocation = timeseries['SubLocationIdentifier']
                q_ts_list_element = Timeseries.Generic_Timeseries(identifier, unique_id, sublocation)
                q_ts_list_element.populate_datasets_for_records(record_start_date, record_end_date)
                
                self.discharge_timeseries_list.append(q_ts_list_element)
                
    def _gather_levels_description(self) -> None:
        """
        Retrieve the levels description from the station description page on SIMs.
        Information can and should be edited on SIMs to match with what the analyzer
        wants.
        """
        self.levels_description = SynchronousSIMsAPISession.get_sims_levels_info(self.site_no)

    def _gather_sensors_list(self, site_no: str)-> None:
         """
         Retrieve a list of published sensors on site. Sensors that are no longer available or in use
         must be removed from the sensors list in AQ.
         """

         sensors_response = SynchronousAquariusAPISession.get_sensors(site_no)
         self.sensors = []
         for sensor in sensors_response["MonitoringMethods"]:
            if Site._has_sublocation(sensor):
                sensor_obj = Sensor(sensor["UniqueId"], sensor["Parameter"], sensor["Method"], sensor["SubLocationIdentifier"])
                self.sensors.append(sensor_obj)
            else:
                sensor_obj = Sensor(sensor["UniqueId"], sensor["Parameter"], sensor["Method"], "")
                self.sensors.append(sensor_obj)

    def has_wwg(self):
        """
        Helper method to check whether site has a wire-weight gage
        """
        for sensor in self.sensors:
            if sensor.method == "Gage height, wire weight gage":
                return True
        return False

    @staticmethod
    def _has_sublocation(individual_sensor_response):
        for parameter in individual_sensor_response:
            if parameter == "SubLocationIdentifier":
                return True
        return False

    def _gather_field_visits(self, record_start_date: datetime.date, record_end_date: datetime.date) -> None:
        """
        Method to gather a list of field visit objects. Information pertinent
        to said field visits will be populated.
        
        Args:
                record_start_date(datetime.date): Date of when the record begins
                record_end_date(datetime.date): Date of when the record ends
            
        """

        field_visit_list = self.api_session.get_field_visits(self.site_no, record_start_date, record_end_date)
        self.field_visits = [] # clear the previous results
        for visit in field_visit_list['FieldVisitDescriptions']:
            visit_date = datetime.strptime(visit['StartTime'][0:10], "%Y-%m-%d")
            visit_obj = Field_Visit.Field_Visit(visit['Identifier'], visit_date, visit['Party'])
            visit_obj.retrieve_records_related_data(self.gage_height_timeseries_list)
            if visit["CompletedWork"]["LevelsPerformed"] == True:
                visit_obj.levels_performed = True
            self.field_visits.append(visit_obj)
          
    def _populate_rating_models(self, record_start_date, record_end_date) -> None:
        """
        Method to retrieve the rating models based on a given date range. Each
        rating model is unique to every discharge related parameter.
        
        Args:
            record_start_date(datetime.date): Date of when the record begins
            record_end_date(datetime.date): Date of when the record ends
        """

        self.rating_model_response = self.api_session.get_discharge_ratings_list(self.site_no)
        rating_model = self.rating_model_response["RatingModelDescriptions"][0]
        rating_model_obj = Rating.Rating_Model(rating_model["Identifier"], self.api_session)
        rating_model_obj.retrieve_info_for_record(record_start_date, record_end_date)
        self.rating_model = rating_model_obj

    def _backcheck_qm_difference(self) -> None:
        """
        Method to be used after a ratings have been populated to check the percent
        difference between discharge measurements and their respective base rating
        at time of collection
        """
        for visit_obj in self.field_visits:
                for qm in visit_obj.dischage_measurements:
                    base_rated_discharge = float(self.api_session.get_discharge_rating_base_output_by_gh(self.rating_model.rating_model_id, qm.mgh, qm.qm_time)["OutputValues"][0])
                    if base_rated_discharge !=0:
                        percent_difference_from_base_rating = ((float(qm.discharge) - base_rated_discharge)/base_rated_discharge)*100
                    else:
                        percent_difference_from_base_rating = 100
                    qm.rating_num_compared = self.rating_model.return_rating_curve_id_for_datetime(qm.qm_time)
                    qm.difference_from_base_rating = percent_difference_from_base_rating
    
    def _gather_ratings_description(self) -> None:
        """
        Retrieve the levels description from the station description page on SIMs.
        Information can and should be edited on SIMs to match with what the analyzer
        wants.
        """
        self.ratings_description = SynchronousSIMsAPISession.get_sims_rating_info(self.site_no)