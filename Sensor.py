class Sensor():
    """
    Class representing a site sensor
    """
    def __init__(self, unique_id: str, parameter: str, method: str, sublocation: str):
        self.unique_id = unique_id
        self.parameter = parameter
        self.method = method
        self.sublocation = sublocation