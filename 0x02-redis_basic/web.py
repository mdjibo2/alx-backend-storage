#!/usr/bin/env python3
"""
Functions for web page handling
"""

import requests
import redis
import functools

# Create a Redis client instance
redis_client = redis.Redis()

def track_calls_and_cache(url):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Track the number of times the URL is accessed
            redis_client.incr(f"count:{url}")

            # Check if the page content is already cached
            cached_content = redis_client.get(f"{url}:content")
            if cached_content:
                return cached_content.decode('utf-8')

            # Fetch the HTML content of the URL
            response = requests.get(url)
            content = response.text

            # Cache the result with a 10-second expiration time
            redis_client.setex(f"{url}:content", 10, content)

            return content

        return wrapper

    return decorator

@track_calls_and_cache("http://slowwly.robertomurray.co.uk/delay/1000/url/https://www.example.com")
def get_page(url: str) -> str:
    """
    Fetches the HTML content of a URL, tracks the number of times it is accessed,
    and caches the result with a 10-second expiration time.
    """
    response = requests.get(url)
    return response.text

