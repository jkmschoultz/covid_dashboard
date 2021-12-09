"""This module runs a Flask web interface which tracks the latest covid data and news for a
location decided in the config file, allowing a user to schedule regular updates to the
information at chosen times, using a scheduler provided in the 'covid_data_handler' module.
"""
import logging
import json
from flask import Flask, render_template, redirect, request
from covid_data_handler import covid_API_request, parse_csv_data, process_covid_csv_data, \
    schedule_covid_updates, scheduler
from covid_news_handling import news_API_request, update_news, remove_article, news_articles
from time_conversions import hhmm_to_seconds, current_time_hhmm

# Load in information from config file
with open('config.json', 'r') as f:
    config = json.load(f)
nation = config['Nation']

scheduled_updates = []  # List of scheduled updates
app = Flask(__name__)  # Flask web app


def make_update(label: str, update_time: str, repeat: str, data: str, news: str) -> list[dict]:
    """Schedules an update with name 'label' to happen in 'interval' seconds. Updates saved covid
    data, news and repeats the update depending on the content of the respective parameters. Adds
    to global 'scheduled_updates' list and returns scheduler queue.
    """
    # Check that at least one option has been chosen
    if not data and not news:
        logging.warning("Attempted to schedule update without selecting any options.")
        return scheduler.queue

    # Check update will be in at least 5 seconds from current time
    interval = hhmm_to_seconds(update_time) - hhmm_to_seconds( current_time_hhmm() )
    if interval < 5:
        logging.warning("Attempted to schedule update too soon.")
        return scheduler.queue

    # Dictionary to store all information about the update
    update = {
        'title': label,
        'content': f"At {update_time} this update will: "
    }

    if data:
        # Schedule data update
        update['data'] = schedule_covid_updates(interval, label)
        update['content'] += "update covid data, "
        logging.info("Covid data update has been scheduled for %s", update_time)

    if news:
        # Schedule news update
        update['news'] = scheduler.enter(interval, 1, update_news, (label,))
        update['content'] += "update covid news, "
        logging.info("News update has been scheduled for %s", update_time)

    if repeat:
        # Schedule update to repeat in 24 hrs
        update['repeat'] = scheduler.enter(
            60*60*24, 1, make_update, (label, update_time, repeat, data, news)
            )
        update['content'] += "repeat in 24 hours, "
        logging.info("Update %s has been scheduled to repeat itself in 24 hours", label)

    # Clean up update content to be displayed
    update['content'] = update['content'][ :len( update['content'] ) - 2 ]

    scheduled_updates.append(update)
    return scheduler.queue


def remove_update(update: str) -> list:
    """Removes 'update' from 'scheduled_updates' list, cancelling all scheduled events included in
    update. Returns scheduler queue.
    """
    for item in scheduled_updates:
        if item['title'] == update:
            if 'data' in item:
                try:
                    # Cancel scheduled data update
                    scheduler.cancel( item['data'][1] )
                    scheduler.cancel( item['data'][2] )
                    logging.info('Covid data update event cancelled')
                except ValueError:
                    logging.info('Covid data update event not cancelled, already completed')

            if 'news' in item:
                try:
                    # Cancel scheduled news update
                    scheduler.cancel( item['news'] )
                    logging.info('News update event cancelled')
                except ValueError:
                    logging.info('Covid news update event not cancelled, already completed')

            if 'repeat' in item:
                try:
                    # Cancel scheduled repeat update
                    scheduler.cancel( item['repeat'] )
                    logging.info('Repeat update event cancelled')
                except ValueError:
                    logging.info('Repeat update event not cancelled, already completed')

            # Remove from list of updates
            scheduled_updates.remove(item)
            logging.info("Scheduled update '%s' has been removed", update)
            return scheduler.queue
    return scheduler.queue


@app.route('/')
def home():
    """Reroutes to /index"""
    return redirect('/index')


@app.route('/index')
def index():
    """Renders index.html template. Catches any form submissions and acts accordingly, depending
    on which requests have been made.
    """
    # HTML form submissions
    cancel_update = request.args.get('update_item')
    notif = request.args.get('notif')
    update_time = request.args.get('update')
    update_label = request.args.get('two')
    repeat_update = request.args.get('repeat')
    data_update = request.args.get('covid-data')
    news_update = request.args.get('news')

    # Cancel unwanted updates
    if cancel_update:
        remove_update(cancel_update)

    # Remove unwanted news articles
    if notif:
        remove_article(notif)

    # Schedule an update if requested
    if update_label:
        if update_time:
            make_update(update_label, update_time, repeat_update, data_update, news_update)
        else:
            logging.warning("Attempted to schedule update with no specified time")

    # Run event scheduler
    scheduler.run(blocking=False)

    # Load visuals and title from config file
    title, favicon, image = config['Title'], config['Favicon'], config['Image']

    # Process stored covid data to display on webpage
    data_filepath, location = config['Covid_data_filepath'], config['Location']  # From config
    local_data = process_covid_csv_data(
        parse_csv_data(f"{ data_filepath }{ location.lower() }_covid_data.csv")
        )
    national_data = process_covid_csv_data(
        parse_csv_data(f"{ data_filepath }{ nation.lower() }_covid_data.csv")
    )

    return render_template('index.html',
        deaths_total="National deaths: " + str( national_data[2] ),
        favicon=favicon,
        hospital_cases="National hospital cases: " + str( national_data[1] ),
        image=image,
        local_7day_infections=local_data[0],
        location=location,
        national_7day_infections=national_data[0],
        nation_location=nation,
        news_articles=news_articles[:4],
        title=title,
        updates=scheduled_updates
        )

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(filename='sys.log', encoding='utf-8', level=logging.INFO)

    # Fetch relevant data and news articles from APIs
    covid_API_request()  # Local data
    covid_API_request(location=nation, location_type='nation')  # National data
    news_API_request()

    app.run()  # Run Flask app
