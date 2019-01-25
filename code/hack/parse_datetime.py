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

    def _get_time(self):
        """
        This function classifies a given time within SDOTs time categories (MORNING, AFTERNOON, EVENING)
        Outputs: time_interval (string)
        """
        return self._get_interval(self.time, morning_start=7, morning_end=9, afternoon_start=9,
            afternoon_end=16, evening_start=16, evening_end=20)



    def _get_interval(self, time, morning_start, morning_end, afternoon_start, afternoon_end,
        evening_start, evening_end):
        """
        Helper method to get a time interval given specific thresholds.
        Inputs: time object, start and end times
        Outputs: time classification
        """
        if time.hour >= morning_start and time.hour <= morning_end:
            time_frame = 'morning'
        elif time.hour > afternoon_start and time.hour <= afternoon_end:
            time_frame = 'afternoon'
        elif time.hour > evening_start and time.hour <= evening_end:
            time_frame = 'evening'
        else:
            time_frame = 'after_hours'
        return time_frame


    def _strip_milliseconds(self):
        """
        This method removed milliseconds from datetime object.
        Inputs: departure time, duration
        Outputs: datetime object
        """
        date_time = parser.parse(self.departure_time).replace(tzinfo=None)
            + dt.timedelta(minutes=float(self.duration))
        return date_time.replace(microsecond=0)