import pylint.lint
pylint_opts = [
    'covid_data_handler',
    'covid_news_handling',
    'main',
    'time_conversions'
    ]
pylint.lint.Run(pylint_opts)
