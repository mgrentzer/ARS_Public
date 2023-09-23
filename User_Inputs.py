from API_Session_V3 import SynchronousAquariusAPISession
from PyQt5.QtWidgets import QMessageBox


class User_Inputs():
    """
    Containerizing class to hold the user's inputs and traits shared across the application's
    widgets. Avoids use of globals and keeps it to filescope.
    """
    
    start_date = None
    end_date = None
    author = ""
    site_no = ""
    record = None
    site = None
    special_notes = ""
    hydro_comp = ""
    gh_tables_list = []
    q_tables_list = []
    successfulSubmissionCnt = 0
    changesWarningCnt = 0
    backup_tables = []
    size_policy = None
    
    def __init__(self):
        pass
    
    @classmethod
    def critical_error_message(cls, msg: str):
        """
        Convenience method to display a critical error message.

        Args:
            msg(str): The message to be displayed to the user.
        """
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(msg)
        error_box.exec_()
    
    @classmethod
    def warning_message(cls, msg):
        """
        Convenience method to display a warning error message.

        Args:
            msg(str): The message to be displayed to the user.
        """
        warning_box = QMessageBox()
        warning_box.setIcon(QMessageBox.Warning)
        warning_box.setWindowTitle("Warning")
        warning_box.setText(msg)
        warning_box.exec_()
    
    @classmethod
    def valid_connection(cls):
        """
        Method to check whether the user is maintaining an encrypted connection to the AQ server.

        Return:
            bool: true for good connection
        """
        try:
            response = SynchronousAquariusAPISession.login()  # Capture the response
            if int(response) >= 400:  # Check for error status codes
                cls.critical_error_message(response.text)  # Display error message
                return False

            else:
                response = SynchronousAquariusAPISession.logout()  # Capture the response
                if int(response) >= 400:  # Check for error status codes
                    cls.critical_error_message(response.text)  # Display error message
                    return False
        
        except Exception as e:
            print(str(e))
            cls.critical_error_message("Error: Cannot Connect to AQ\n\nCheck your connection and VPN.")
            return False

        return True

