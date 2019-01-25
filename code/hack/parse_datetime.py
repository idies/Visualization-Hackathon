from dateutil import parser
import datetime as dt


class ParseDatetime(object):
    """
    This class parses a departure timestamp 9string), and gives time interval (MORNING, AFTERNOON 
    or EVENING), type of day (WEEKDAY or WEEKEND), and parking time interval (blocks of time with distinct
    parking rates). For details of the threasholds for all time intervals, refer to the constants file.
    """
    def __init__(self, departure_time, duration=0):
        """
        Inputs: departure time (string), duration (float), parking (boolean, default=True)
        Outputs: time_interval (string) and day_type (string)
        If desired, user can choose to set a parking_time_interval (string)
        """
        self.departure_time = departure_time
        self.duration = duration
        self.date_time = self._strip_milliseconds()
        self.time = self.date_time.time()
        self.date = self.date_time.date()
        self.day_type = self._get_day()


    def _get_day(self):
        """
        Takes in a date_time + trip duration and classifies as WEEKDAY or WEEKEND
        Outputs: day_type 
        """
        if self.date.weekday() < cn.SATURDAY:
            day_type = 'weekday'
        else:
            day_type = 'weekend'
        return day_type


    def _strip_milliseconds(self):
        """
        This method removed milliseconds from datetime object.
        Inputs: departure time, duration
        Outputs: datetime object
        """
        date_time = parser.parse(self.departure_time).replace(tzinfo=None)
            + dt.timedelta(minutes=float(self.duration))
        return date_time.replace(microsecond=0)