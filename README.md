# Covid Dashboard
This program provides a personalised covid dashboard for users. Users can use the web interface to see the latest covid figures in a chosen location and country, as well as relevant news articles about coronavirus.

    python3 main.py

Run the 'main' module with a python interpreter to start the web app, which will then be accessible at the local http://127.0.0.1:5000/ domain. The data used by the server is gotten from the Public Health England API, and is stored by default in the 'data' directory. The news articles are gotten from NewsAPI.org. NB: Users must register for an API key for the news API, and use this to fill the 'API_KEY' field in the configuration file. The links to these APIs are provided at the bottom of this README for referral. Updates to the stored data and news articles that are displayed on the web page can be scheduled through the interface.

## Configuration
A 'config.json' file is included to allow user customization of the program. The different options explained in order of importance are:

    NEWS API KEY: the API key used to access the news API. Please register for an API key on the NewsAPI.org website and use this to run the program.

    Location: the location the user wishes to display covid data for.

    Location type: the type of location for the location mentioned above. This must be one of 'region', 'nhsRegion', 'utla' (Upper-tier local authority), or 'ltla' (Lower-tier local authority). Please refer to the PHE API documentation for more information.

    Nation: the country to display national covid statistics for.

    Covid data filepath: the directory that will be used to store the covid data used by the program.

    Headers: the headers used when getting statistics from the PHE API. IE, if a user wishes to use a different measurement of deaths or hospital cases provided in the API, these can be changed here. Please refer to the API documentation to find the list valid metrics.

    Favicon: the favicon that is displayed on the webpage.

    Image: the image displayed at the top of the webpage.

    Title: the title displayed on the website.

## Runtime
Once running, the server will create a 'sys.log' file in the main working directory which displays a log of all events that happen during runtime. The 'main' module makes use of functionality provided by the 'covid_data_handler', 'covid_news_handling' and 'time_conversions' modules to find and interpret covid data and news articles. The 'main' module itself is responsible for running the interactive web application, with the help of the 'flask' package. Scheduling updates to the data and news articles will, when executed, refresh the stored data structures with information gotten from new API requests. The program was written using Python version 3.9.7 and also makes use of the following python packages:
    
    - flask
    - io
    - json
    - logging
    - numpy
    - pandas
    - requests
    - sched
    - time
    - uk_covid19 (PHE API)
    - pylint **
    - pytest **

## Prerequisite packages
Please ensure these packages are installed with the python interpreter used when running the program. This can be done using
    
    pip3 install uk_covid19 requests pandas numpy flask pylint pytest
** To run the 'linter' testing module the 'pylint' package is required, and 'pytest' is needed for unit testing.

## Testing
The 'tests' directory includes testing modules for the functionality of the different modules, testing data functionality against the 'nation_2021-10-28.csv' static file, as well as the 'linter' module which checks proper code convention is used. Run the 'linter' module with the python interpreter from the main project directory to check the grade given for code convention (ie 'python3 tests/linter.py'). The unit testing modules can be run using:

    python3 -m pytest

## Directories
The 'templates' directory is where the index html page is stored, as required when using flask, and images/icons are stored in the 'static' directory.

## Links
Github repository: https://github.com/jkmschoultz/covid_dashboard

Covid data API link: https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/

News API link: https://newsapi.org

This program was written by: Johan Schoultz at University of Exeter.