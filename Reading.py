from datetime import timedelta
import Dataset


class Reading():
    """
    Class object representing a generic reading.
    """
    def __init__(self, parameter: str, monitoring_method: str, reading_type: str, datetime, value: float, sublocation = "", comment: str = "") -> None:
        """
        Intialization method
        
        Args:
            parameter(str): The parameter for which the reading represents
            monitoring_method(str): The method of which the reading was collected
            reading_type(str): The type of reading whether it be primary reference, routine recorder, or reference reading
            datetime(datetime.datetime): Datetime of the reading
            value(float): Reading's value
            comment: Any miscellaneous comments the visitor recorded about the visit
        """
        self.parameter = parameter
        self.monitoring_method = monitoring_method
        self.reading_type = reading_type
        self.datetime = datetime
        self.value = float(value)
        self.discrepancy = None
        self.sublocation = sublocation
        self.comment = comment  
    
    @staticmethod
    def _retrieve_bordering_dataset(reading_datetime, ts_id: str) -> Dataset.Dataset:
        """
        Helper method to retrieve the timeseries dataset surrounding a particular reading for later comparison to determine
        the recorder unit value (uv) prior the reading and then after the reading
        
        Args:
            reading_datetime(datetime.datetime): Datetime of when the reading occurred
            ts_id(str): Unique timeseries ID for which the reading is being compared to
        """
        ONE_DAY = 1
        
        one_day_timedelta = timedelta(days=ONE_DAY)
        day_prior = reading_datetime - one_day_timedelta
        day_after = reading_datetime + one_day_timedelta
        bordering_dataset = Dataset.Dataset(ts_id, day_prior, day_after)
        bordering_dataset._gather_data()
        return bordering_dataset
    
    @staticmethod
    def _return_recorder_data_point_prior_to_reading(reading_datetime, bordering_dataset: Dataset.Dataset) -> Dataset.Data_Point:
        """
        Helper method to determine a Data_Point object representing the unit value prior to the reading.
        
        Args:
            reading_datetime(datetime.datetime): Datetime of when the reading occurred
             bordering_dataset(Dataset.Dataset): Dataset containing data_points for the day prior, day of reading, and day after the reading
             
        Return:
            prior_pt(Dataset.Data_Point): Data_Point object for the unit value occurring just prior to the reading
        """
        DAYS_IN_YEAR = 365
        
        shortest_duration = timedelta(days=DAYS_IN_YEAR)
        prior_pt = None
        
        for pt in bordering_dataset.data:
            if (reading_datetime - pt.datetime) < shortest_duration and (reading_datetime - pt.datetime) >= timedelta(seconds=0):
                shortest_duration = reading_datetime - pt.datetime
                prior_pt = pt
        
        return prior_pt
    
    @staticmethod
    def _return_discrepancy(reading_datetime, reading_value: float, prior_uv: Dataset.Data_Point, next_uv: Dataset.Data_Point) -> float:
        """
        Helper method to determine the discrepancy of a reading provided its datetime, value, a Data_Point representation of
        the previous occurring unit value, data_point representation of the next unit value.
        
        Args:
            reading_datetime(datetime.datetime): Datetime of when the reading occurred
            readign_value(float): The reading's value
            prior_uv(Dataset.Data_Point): The Data_Point object representation of the unit value occurring at or just prior to the reading
            next_uv(Dataset.Data_Point): The Data_Point object representation of the unit value occurring after the reading
             
        Return:
            discrepancy(float): The reading's discrepancy
        """
        discrepancy = None
        if next_uv != None:
            bordering_uv_diff = next_uv.datetime - prior_uv.datetime
            time_elapsed_in_window = reading_datetime - prior_uv.datetime
            percent_in_time_elapsed = time_elapsed_in_window/bordering_uv_diff
            
            value_diff = float(next_uv.value) - float(prior_uv.value)
            interpolated_value = float(prior_uv.value) + (percent_in_time_elapsed * value_diff)
            discrepancy = round(interpolated_value - reading_value, 3)
        return discrepancy
    
    def check_discrepancy(self, gh_ts_list: str) -> None:
        """
        Method to retrieve the discrepancy of a particular reading provided a particular timeseries ID.
        
        Args
            ts_id(str): Unique timeseries ID for which the reading is being compared to
        """
        
        if len(gh_ts_list) == 1:
            # dataset containing data for the day prior and after the reading's occurence, used to acquire record uvs before and after the reading
            bordering_dataset = Reading._retrieve_bordering_dataset(self.datetime, gh_ts_list[0].TS_unique_id)
            
            prior_uv_data_point = Reading._return_recorder_data_point_prior_to_reading(self.datetime, bordering_dataset)
            next_uv_data_point = prior_uv_data_point.next
            
            self.discrepancy = Reading._return_discrepancy(self.datetime, self.value, prior_uv_data_point, next_uv_data_point)
        
        elif len(gh_ts_list) > 1:
            for gh_ts in gh_ts_list:
                if self.sublocation == gh_ts.TS_sublocation:
                    # dataset containing data for the day prior and after the reading's occurence, used to acquire record uvs before and after the reading
                    bordering_dataset = Reading._retrieve_bordering_dataset(self.datetime, gh_ts.TS_unique_id)
                    
                    prior_uv_data_point = Reading._return_recorder_data_point_prior_to_reading(self.datetime, bordering_dataset)
                    next_uv_data_point = prior_uv_data_point.next
                    
                    self.discrepancy = Reading._return_discrepancy(self.datetime, self.value, prior_uv_data_point, next_uv_data_point)