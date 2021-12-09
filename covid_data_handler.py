"""This module handles covid data, including parsing and processing, and requesting the latest
covid data from Public Health England's API, as well as scheduling updates to saved covid data.
"""
from io import FileIO
import json
import sched
import time
import logging
import requests
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
from uk_covid19 import Cov19API

# Load relevant data from config file
with open('config.json', 'r') as f:
    config = json.load(f)
area, area_type = config['Location'], config['Location_type']
death_header, hospital_header, cases_header = (
    config['Headers']['Deaths'],
    config['Headers']['Hospital_cases'],
    config['Headers']['New_cases']
)

# Scheduler to schedule updates to covid data
scheduler = sched.scheduler(time.time, time.sleep)


def covid_API_request(location: str=area, location_type: str=area_type) -> dict:
    """Returns latest Covid data from Public Health England's Covid-19 API as a dictionary,
    filtering by 'location' and 'location_type'. Saves data as csv file in the configured filepath.
    """
    filepath = config['Covid_data_filepath']  # Where covid data will be saved

    # Filters to be applied to API request
    filters = [
        f"areaType={location_type}",
        f"areaName={location}"
    ]

    # Structure of data to receive from API request
    structure = {
        "areaCode": "areaCode",
        "areaName": "areaName",
        "areaType": "areaType",
        "date": "date",
        death_header: death_header,
        hospital_header: hospital_header,
        cases_header: cases_header
    }

    try:
        # Instantiate API and save covid data as file
        api = Cov19API(filters=filters, structure=structure)
        data = api.get_json(as_string=True)
        api.get_csv(save_as=f"{ filepath }{ location.lower() }_covid_data.csv")
        logging.info("Retrieved data for %s from PHE API", location)
        return json.loads(data)

    except requests.RequestException:
        logging.warning("PHE Covid API could not be reached")
        return {}


def parse_csv_data(csv_filename: FileIO) -> list[str]:
    """Returns contents of 'csv_filename' as list of strings by row"""
    try:
        return open(csv_filename).readlines()

    except FileNotFoundError:
        logging.warning("File with path '%s' not found", csv_filename)
        return []


def parse_json_data(data: dict) -> list[str]:
    """Reformats json 'data' to list of strings, matching format of 'parse_csv_data()' function.
    """
    # Load json into pandas framework
    data_list = []
    df = DataFrame.from_dict( data['data'] ).astype(str)
    keys, values = df.columns.tolist(), df.values.tolist()

    # Add headers as string separated by commas
    data_list.append( ','.join(keys) )
    for value in values:
        # Add each row of values as string separated by commas
        data_list.append( ','.join(value).replace('None', '').replace('nan', '') )

    return data_list


def process_covid_csv_data(covid_csv_data: list[str]) -> tuple[int]:
    """Returns number of new cases in the last 7 days, current number of hospital cases and
    number of deaths from data stored in 'covid_csv_data'. Expects data format as list of
    strings, as would be returned from 'parse_csv_data()' or 'parse_json_data()'.
    """
    # Check if dataset is empty
    if not covid_csv_data:
        logging.warning("Dataset is empty")
        return 0, 0, 0

    try:
        # Load data into a framework using pandas
        df = pd.DataFrame(
            columns=[ x.strip() for x in covid_csv_data[0].split(',') ],
            data=[ row.split(',') for row in covid_csv_data[1:] ]
        )

        # Reorganise and format data in framework
        for column in df.columns:
            df[column] = df[column].str.strip()
        df = df.replace('', np.nan, regex=True)
        df = df.sort_values(by='date', ascending=False)

        # Rename columns for readability
        df = df.rename(columns={
            death_header: 'deaths',
            hospital_header: 'hospitalCases',
            cases_header: 'newCases'
        })
        location = df.areaName[0]
    except KeyError:
        logging.warning("Dataset missing necessary data")
        return 0, 0, 0
    except IndexError:
        logging.warning("Dataset could not be processed properly")
        return 0, 0, 0

    try:
        # Find number of deaths
        deaths = int( df.deaths[ df.deaths.first_valid_index() ] )
    except KeyError:
        logging.info("Total deaths in %s could not be found", location)
        deaths = 0

    try:
        # Find number of hospital cases
        hospital_cases = int( df.hospitalCases[ df.hospitalCases.first_valid_index() ] )
    except KeyError:
        logging.info("Hospital cases in %s could not be found", location)
        hospital_cases = 0

    try:
        # Find new cases in last 7 days
        last7 = 0
        last7_start = df.newCases.first_valid_index() + 1  # Skip most recent entry
        for day in range(last7_start, last7_start + 7):
            last7 += int( df.newCases[day] )
    except KeyError:
        last7 = 0
        logging.info("Data for new cases in %s over last 7 days not found", location)
    except ValueError:
        logging.info("Data for new cases in %s in most recent 7 days is incomplete", location)

    return last7, hospital_cases, deaths


def schedule_covid_updates(update_interval: int, update_name: str) -> tuple[str, sched.Event]:
    """Schedules a covid data update called 'update_name'. Data to be updated after time
    'update_interval'. Updates local and national data. Returns tuple of the update name and
    scheduled events.
    """
    nation = config['Nation']  # From config file
    event1 = scheduler.enter(update_interval, 1, covid_API_request)
    event2 = scheduler.enter(update_interval, 1, covid_API_request, (nation, 'nation'))
    return update_name, event1, event2
