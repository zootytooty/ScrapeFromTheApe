"""
Title: Datetime Helpers
Desc:  A collection of utility functions to parse dates & times
"""

import re
from datetime import datetime


def time_parser(time):
    """Converts timestamps into a consistent computer usable form.
    Handles timestamps of the format:
        - 1.00PM (or AM)
        - 1:00PM (or AM)
        - 1PM (or AM)
        - 13:00

    Args:
        time (str): Timestamp to be standardised 
    
    Returns:
        str: Timestamp in format HH:MM
    """

    time = time.lower()

    # Idenfiy delimiter 
    raw_time = time.replace('pm','').replace('am','').strip()
    if '.' in time:
        delimiter = '.'
    elif ':' in time:
        delimiter = ':'
    else:
        delimiter = ':'
        raw_time += ':00'

    # Identify whether it's in 12hr or 24hr time
    if 'pm' in time:
        time_to_parse = "{} pm".format(raw_time)
        time_format = "%I{}%M %p".format(delimiter)
        
        clean_time = datetime.strptime(time_to_parse, time_format).strftime("%H:%M")

    elif 'am' in time:
        time_to_parse = "{} am".format(raw_time)
        time_format = "%I{}%M %p".format(delimiter)
        
        clean_time = datetime.strptime(time_to_parse, time_format).strftime("%H:%M")
        
    else:
        clean_time = datetime.strptime(time, "%H:%M").strftime("%H:%M")


    return clean_time


def get_timestamp(time_string):
    """Identified & extracts a timestamp from a string
    
    The currently supported formats are:
        - 01am
        - 1am
        - 12am
        - 12 am
        - 1 am
        - 12:12am
        - 12:12 am
        - 12.12am
        - 12.12 am
    
    Args:
        time_string (str): String that contains a timestamp
    
    Returns:
        str: Timestamp in format HH:MM
    """
    matches = re.findall(r"(\d{0,2}(?:.|:)\d{0,2}\s?(?:AM|PM|pm|am))|(\d{2}(?:.|:)\d{0,2})", time_string)
    matches = matches[0]
    matches = [x.strip() for x in matches if x != '']
    if len(matches) == 1:
        match = matches[0]
        match = time_parser(match)
        return match
    else:
        return None


