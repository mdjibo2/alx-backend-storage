#!/usr/bin/env python3
"""
This module contains a function for retrieving the content of a web page.
"""

import requests
import time
from functools import wraps

CACHE_EXPIRATION = 10  # seconds


def track_calls_and_cache(url):
    cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if url in cache and time.time() - cache[url]["time"] < CACHE_EXPIRATION:
                cache_hit = True
                response = cache[url]["response"]
            else:
                cache_hit = False
                response = func(*args, **kwargs)
                cache[url] = {"response": response, "time": time.time()}
            count_key = f"count:{url}"
            if count_key in cache:
                cache[count_key] += 1
            else:
                cache[count_key] = 1
            return response, cache_hit
        return wrapper
    return decorator


@track_calls_and_cache("http://slowwly.robertomurray.co.uk")
def get_page(url):
    response = requests.get(url)
    return response.content.decode("utf-8")


if __name__ == "__main__":
    print(get_page("http://slowwly.robertomurray.co.uk"))
