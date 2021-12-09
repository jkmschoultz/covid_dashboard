"""This module handles and stores covid news articles which are gotten from a news API.
"""
import json
import logging
import requests

# Data structures to store news articles and removed articles
news_articles, removed_articles = [], []

def news_API_request(covid_terms: str='Covid COVID-19 coronavirus') -> list[dict]:
    """Queries news API for each term in 'covid_terms'. Saves list of articles found into global
    variable 'news_articles' and returns this list.
    """
    # Load API key from config file
    with open('config.json') as f:
        config = json.load(f)
    API_KEY = config['NEWS_API_KEY']

    for term in covid_terms.split():

        # Parameters to use in GET request
        params = {
            'q': term,
            'apiKey': API_KEY
        }
        try:
            # Make GET request to API for each term in 'covid_terms'
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params=params
            )

            for article in response.json()['articles']:
                # Add each unique article to list
                if article not in news_articles:
                    # Remove ugly end part of article content
                    stop = article['content'].index('[+') - 1
                    article['content'] = article['content'][:stop]
                    news_articles.append(article)
            logging.info("News articles retrieved from News API for term '%s'", term)

        except KeyError:
            logging.warning("Could not find articles in News API response for search '%s'", term)
        except requests.RequestException:
            logging.warning("Could not search news API for '%s' due to connection error", term)

    return news_articles


def remove_article(article: str) -> list[str]:
    """Removes news article with title 'article' from 'news_articles' list. Adds title to global
    'removed_articles' list and returns it.
    """
    removed_articles.append(article)
    for item in news_articles:
        if item['title'] == article:
            news_articles.remove(item)
            logging.info("News article '%s' has been removed", article)
    return removed_articles


def update_news(update_name: str) -> list[dict]:
    """Refreshes global 'news_articles' list with a new API request. Ensures 'removed_articles'
    do not reappear. Returns the updated list of articles.
    """
    news_API_request()
    for article in news_articles:
        if article['title'] in removed_articles:
            news_articles.remove(article)
    logging.info("News articles update executed as part of '%s'", update_name)
    return news_articles
