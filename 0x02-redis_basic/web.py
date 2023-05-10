#!/usr/bin/env python3
"""
Functions for web page handling
"""

import requests
import redis
import functools


# Connect to Redis
REDIS = redis.Redis()


# Define decorator to cache and count calls
def cache_count_calls(func):
    @functools.wraps(func)
    def wrapper(url):
        """
        Wrapper function to cache and count calls to the decorated function.
        """
        key = f'count:{url}'
        count = REDIS.get(key)
        if count is None:
            count = 1
        else:
            count = int(count) + 1
        REDIS.set(key, count, ex=10)

        # Check if response is already cached
        html = REDIS.get(url)
        if html is not None:
            return html.decode('utf-8')

        # Fetch HTML and cache response
        response = requests.get(url)
        html = response.text
        REDIS.set(url, html, ex=10)
        return html

    return wrapper


# Decorate get_page with cache_count_calls
@cache_count_calls
def get_page(url: str) -> str:
    """
    Fetches the HTML content of a URL, caches it, and counts the number of calls.
    """
    response = requests.get(url)
    return response.text

