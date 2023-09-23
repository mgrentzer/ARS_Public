from API_Session_V3 import SynchronousAquariusAPISession
from datetime import datetime
import Dataset

class Generic_Timeseries():
    """
    Class representing a single Aquarius gage height timeseries
    
    Each timeseries pertains to a dataset with corrections and edits independent
    of other timeseries irrespective if there exists multiple for the same site.
    """
    def __init__(self, TS_identifier: str, TS_unique_id: str, TS_sublocation: str, api_session: SynchronousAquariusAPISession = None) -> None:
        """
         Initialize the Gage_Height_Timeseries object.

        Args:
            GH_TS_identifier(str): The NWIS stream site name with mention of stream name and relative location
            GH_TS_unique_id(str): The Aquarius assigned alphanumeric ID for the timeseries
            GH_TS_sublocation(str): The sublocation provided by the LDM creator, usually upstream/downstream or type of recorder
            api_session(SynchronousAquariusAPISession): The api_session, if provided, that connects to the NWIS family of web services
        """
        
        self.TS_identifier = TS_identifier
        self.TS_unique_id = TS_unique_id
        self.TS_sublocation = TS_sublocation
        self.record_dataset: Dataset.Dataset = None
        self.water_year_datasets: dict[str: Dataset.Dataset] = {}
        self.api_session = api_session or SynchronousAquariusAPISession()
    
    def populate_datasets_for_records(self, record_start_date, record_end_date) -> None:
        """
        Populate the record and water year datasets based upon the provided record
        dates
        
        Args:
            record_start_date(datetime.date): The starting date of the record being made
            record_end_date(datetime.date): The starting date of the record being made
        """
        self._gather_record_period_dataset(record_start_date, record_end_date)
        self._gather_water_year_dataset_list(record_start_date, record_end_date)
        
    def _gather_record_period_dataset(self, record_start_date: datetime.date, record_end_date: datetime.date) -> None:
        """
        Method to gather the dataset for the record period, including all 
        corrections and edits associated with it.
        
        Args:
            record_start_date(datetime.date): The record's start date
            record_end_date(datetime.date): The record's end date
        """
        self.record_dataset = Dataset.Dataset(self.TS_unique_id, record_start_date, record_end_date, self.api_session)
        self.record_dataset.gather_data_for_records()

    @staticmethod
    def _determine_water_year_by_date(checked_date: datetime.date) -> datetime.year:
        """
        Helper method to provide which water year a given date falls on. This used
        on the provided record date to figure out which water year datasets are needed
        for the end product.
        
        Args:
            checked_datetime(datetime.date): The date to check for which WY it belongs to
            
        Returns:
            datetime.year: The water year that corresponds to the provided date.
        """
        if(checked_date.month < 10):
            return checked_date.year
        else:
            return checked_date.year + 1


    def _populate_wy_dataset_by_year(self, year: datetime.year):
        """
        Helper method to create, populate, and return a dataset object for a water-year
        using a provided year number.
        
        Args:
            year(datetime.year): The year for which timeseries data is collected for
        """
        
        WY_STARTING_DAYTIME = "-10-1 00:00:00"
        WY_ENDING_DAYTIME = "-09-30 23:59:59"
        WY_start_datetime = datetime.strptime(str(year-1) + WY_STARTING_DAYTIME, "%Y-%m-%d %H:%M:%S")
        WY_end_datetime = datetime.strptime(str(year) + WY_ENDING_DAYTIME, "%Y-%m-%d %H:%M:%S")
        WY_dataset = Dataset.Dataset(self.TS_unique_id, WY_start_datetime, WY_end_datetime, self.api_session)
        WY_dataset.gather_data_for_records()
        return WY_dataset
        

    def _gather_water_year_dataset_list(self, record_start_date: datetime.date, record_end_date: datetime.date) -> None:
        """
        Gather the datasets for all water years that the provided Record object encompasses.
        A list of datasets encompassing the bounds of each water year will be assigned to the Gage_Height_Timeseries object.

        Args:
            record_start_date(datetime.date): The record's start date
            record_end_date(datetime.date): The record's end date
            api_session (SynchronousAquariusAPISession): The api_session, if provided, that connects to the NWIS family of web services.
        """
        
        # Below are the water years the record starts in and ends in
        record_starting_water_year = Generic_Timeseries._determine_water_year_by_date(record_start_date)
        record_ending_water_year = Generic_Timeseries._determine_water_year_by_date(record_end_date)
        
        # For each water year the record encompass, gather data, append to list of WY datasets
        for water_year in range(record_starting_water_year, record_ending_water_year + 1):
            WY_dataset = self._populate_wy_dataset_by_year(water_year)
            self.water_year_datasets[str(water_year)] = WY_dataset
 