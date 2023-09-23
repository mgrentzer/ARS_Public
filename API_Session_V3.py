""""
Author: Michael Grentzer

This module serves an interface to communicate and request data from the SIMs
web environment.

©2023 Michael Grentzer <mgrentzer@usgs.gov>

Disclaimer: For internal use only, reuse or dissemination of elements of the
 below code can be made with permission of the original author.
"""

from abc import ABC, abstractmethod
from os import environ
import requests
import logging
import xml.etree.ElementTree as ET
import re
import time

DEBUG = True

class AquariusAPISession(ABC):
    """
    Abstract class representing an individual session of HTTP request interations
    to Aquarius (AQ). I anticipate that this may be made Asynchronous
    later.
    """
    aq_username = environ.get("API_KEY")
    aq_password = environ.get("API_PASSWORD")
    aq_locale = "Louisville"
    aq_server_type = "ts" # ts = live server, tsqa = test server
    
    GET = "get"
    DELTETE = "delete"
    POST = "post"
    
    
    @classmethod
    @abstractmethod
    def configure_logging(cls):
        """
        Class method to configure the log file for a module's APISession.
        """
        pass
    
    @classmethod
    @abstractmethod
    def _make_aq_request(cls, rest_type: str, api_type: str, params):
        """
        Helper method to handle retrieving json data from AQ's REST Service
        
        Args:
            rest_type(str): The REST API request type, e.g. Post, Get, Delete, etc.
            api_type(str): The type of request being made, ex: GetSiteInfo
            params({str:str}): A dictionary of parameters relevant to request
                
        Returns:
            str: utf-8 decoded string of the json response from SIMs
        """
        pass
    
    @classmethod
    @abstractmethod
    def login(cls) -> int:
        """
        Method to login to Aquarius for a synchronous session of HTTP requests.
        
        Return:
            int: The status code received back from the login request
        """
        pass
    
    @classmethod
    @abstractmethod
    def logout(cls) -> int:
        """
        Method to logout to Aquarius for a synchronous session of HTTP requests.
        A 200 return code is successful
        
        Return:
            int: The status code received back from the logout request
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_site_info(cls, site_no: str):
        """
        Method to retrieve the site's name and unique ID associated with it in AQ
        provided an NWIS registered site number.
        
        Args:
            site_no(str): The 8- or 15-digit site number assigned associated with NWIS
        
        Returns:
            (str, str): A tuple consisting of the site name and its unique AQ ID
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_gage_height_timeseries_list(cls, site_no: str):
        """
        Method to retrieve the list of gage height timeseries that are
        published and instantaneous readings.
        
        Args:
            site_no(str): The 8- or 15-digit site number assigned associated with NWIS
        
        Returns:
            [str]: A list of timeseries and their attributes
        """
        pass
     
    @classmethod
    @abstractmethod
    def get_timeseries_data(cls, ts_unique_id: str, query_from, query_to) -> str:
        """
        Method to retrieve the gage height data from a provided window
        of time provided the timeseries' unique ID and time window.
        
        Args:
            ts_unique_id(str): The unique ID associated wtih a timeseries provided by AQ
            query_from(datetime.date): The start date of data acquisition
            query_to(datetime.date): The end date of data acquisition
        
        Returns:
            str: A list of timeseries data formatted in JSON format
        """
        pass
        
    @classmethod
    @abstractmethod
    def get_gh_corrections_list(cls, ts_unique_id: str, query_from, query_to) -> str:
        """
        Method to retrieve the gage height data from a provided window
        of time provided the timeseries' unique ID and time window.
        
        Args:
            ts_unique_id(str): The unique ID associated wtih a timeseries provided by AQ
            query_from(datetime.date): The start date of data acquisition
            query_to(datetime.date): The end date of data acquisition
        
        Returns:
            str: A list of timeseries corrections formatted in JSON format
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_field_visits(cls, site_no: str, query_from, query_to) -> str:
        """
        Method to retrieve a set of field visits made at provided site number for
        a provided span of time.
        
        Args:
            ts_unique_id(str): The unique ID associated wtih a timeseries provided by AQ
            query_from(datetime.date): The start date of data acquisition
            query_to(datetime.date): The end date of data acquisition
                
        Returns:
            str: A list of field visits formatted in JSON format
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_field_visit_data(cls, field_visit_id: str) -> str:
        """
        Method to retrieve a data from a provided field visit ID .
        
        Args:
            field_visit_id(str): The unique ID for a specified field visit.
                
        Returns:
            str: A list of data for a provided field visit formatted in JSON format
        """
        pass

    @classmethod
    @abstractmethod
    def get_sensors(cls, site_no: str) -> str:
        """
        Method to retrieve a list of sensors at a provided site.
        
        Args:
            site_no(str): The 8- or 15-digit site number assigned associated with NWIS.
                
        Returns:
            str: A list of data for a provided field visit formatted in JSON format
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_discharge_ratings_list(cls, site_no: str) -> str:
        """
        Method to retrieve a list of sensors at a provided site.
        
        Args:
            site_no(str): The 8- or 15-digit site number assigned associated with NWIS.
                
        Returns:
            str: A list of data for a provided field visit formatted in JSON format
        """
        pass

    @classmethod
    @abstractmethod
    def get_discharge_rating_model_info(cls, rating_model_id: str, query_from = "", query_to = "") -> str:
        """
        Method to retrieve a list of sensors at a provided site.
        
        Args:
            rating_model_id(str): ID of the rating model used to computed discharge
            query_from(datetime.date): The start date of data acquisition
            query_to(datetime.date): The end date of data acquisition
                
        Returns:
            str: A list of data for a provided field visit formatted in JSON format
        """
        pass

    @classmethod
    @abstractmethod
    def get_discharge_rating_base_output_by_gh(cls, rating_model_id: str, gage_height: float, datetime) -> str:
        """
        Method to get the discharge at a particular stage value at a particular time. The use of time is agnostic to
        rating curve, so this simplifies trying to determine which curve is effective at a given time.
        
        Args:
            rating_model_id(str): ID of the rating model used to computed discharge
            gage_height(float): The gage height being checked
            datetime(datetime.datetime): The time at which the discharge is being checked
        """
        pass

class SynchronousAquariusAPISession(AquariusAPISession):
    """
    Concrete class implementation of APISession as a session of HTTP requests 
    performed in synchronous fashion.
    """
    # *** Redacted ***

class SIMsAPISession(ABC):
    """
    Abstract class/interface representing an individual session of HTTP request interations
    to both SIMs. I anticipate that this may be made Asynchronous later.
    """
    @classmethod
    @abstractmethod
    def configure_logging(cls):
        """
        Class method to configure the log file for a module's APISession.
        """
        pass

    @classmethod
    @abstractmethod
    def _make_sims_request(cls, api_type: str, params):
        """
        Helper method to handle retrieving xml data from SIM's webservices
        
        Args:
            api_type(str): The type of request being made, ex: GetSiteInfo
            params({str:str}): A dictionary of parameters relevant to request
                
        Returns:
            str: utf-8 decoded string of the xml response from SIMs
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_office_info_by_wsc(cls, wsc_id: int) -> str:
        """
        Method to retrieve info for all offices within a provided water science
        center.
        
        Args:
            wsc_id(int): The unique ID for the WSC being queried for office info
        
        Returns:
            str: utf-8 decoded string of the xml response from SIMs
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_sites_by_office(cls, wsc_id: int, office_id: int) -> str:
        """
        Method to retrieve site information for provided office. The WSC ID
        must be included as part of SIMs SOP.
        
        Args:
            wsc_id(int): The unique ID for the WSC being queried for office info
            office_id(int): The unique ID for the office being queried for site info
        
        Returns:
            str: utf-8 decoded string of the xml response from SIMs
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_elements_by_site(cls, doc_type: str, site_no: str, agency_cd: str) -> str:
        """
        Method to retrieve and return the station documentation from SIMs for a
        a provided site.
        
        Args:
            doc_type(str): The type of document being retrieved, e.g. Station Desc., Manuscript, ect.
            site_no(str): The 8- or 15-digit site number assigned associated with NWIS
            agency_cd(str): The code for which agency is assigned to operate the site, 99.99% the time is USGS
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_sims_site_id(cls, site_no) -> str:
        """
        Method to retrieve and return the unique ID associated with a provided 
        USGS site number.
        
        Args:
            site_no(str): The 8- or 15-digit site number assigned associated with NWIS
            
        Returns:
            str: The unique ID for the provided site number given by SIMs
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_sims_levels_info(cls, site_no) -> str:
        """
        Method to retrieve the station's levels description from SIMs.
        
        Args:
            site_no(str): The 8- or 15-digit site number assigned associated with NWIS
        
        Return:
            str: A well formatted string version of the station's levels description.
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_sims_rating_info(cls, site_no) -> str:
        """
        Method to retrieve the station's rating descriptions from SIMs.
        
        Args:
            site_no(str): The 8- or 15-digit site number assigned associated with NWIS
        
        Return:
            str: A well formatted string version of the station's levels description.
        """
        pass
    
class SynchronousSIMsAPISession(SIMsAPISession):
    """
    Concrete class implementation of APISession as a session of HTTP requests 
    performed in synchronous fashion.
    """
    # *** Redacted ***
    