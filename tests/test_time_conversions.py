from time_conversions import minutes_to_seconds
from time_conversions import hours_to_minutes
from time_conversions import hhmm_to_seconds
from time_conversions import hhmmss_to_seconds
from time_conversions import current_time_hhmm

def test_minutes_to_seconds():
    seconds = minutes_to_seconds('2')
    assert seconds == 120

def test_hours_to_minutes():
    minutes = hours_to_minutes('1')
    assert minutes == 60

def test_hmm_to_seconds():
    seconds = hhmm_to_seconds('01:05')
    assert seconds == 65*60

def test_hhmmss_to_seconds():
    seconds = hhmmss_to_seconds('01:05:03')
    assert seconds == 65*60 + 3

def test_current_time_hhmm():
    current = current_time_hhmm()
    assert isinstance(current, str)
