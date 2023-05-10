#!/usr/bin/env python3
""" Cache module
"""

import redis
import uuid
import functools
from typing import Callable


def count_calls(func: Callable) -> Callable:
    """Decorator that counts how many times a function
    has been called.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        key = func.__qualname__
        self._redis.incr(key)
        return func(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator that stores the history of inputs and outputs
    for a particular function.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        inputs_key = f"{method.__qualname__}:inputs"
        outputs_key = f"{method.__qualname__}:outputs"

        input_str = str(args)
        self._redis.rpush(inputs_key, input_str)

        output = method(self, *args, **kwargs)
        self._redis.rpush(outputs_key, output)

        return output
    return wrapper


class Cache:
    """ Cache class
    """
    def __init__(self):
        """ Constructor method
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: bytes) -> str:
        """ Store data in Redis and return a unique id
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str) -> bytes:
        """ Get data from Redis by key
        """
        return self._redis.get(key)

    def get_str(self, key: str) -> str:
        """ Get data from Redis by key as string
        """
        return self._redis.get(key).decode('utf-8')

    def get_int(self, key: str) -> int:
        """ Get data from Redis by key as integer
        """
        return int(self._redis.get(key).decode('utf-8'))


def replay(fn: Callable):
    """ Display the history of calls of a particular function
    """
    r = redis.Redis()
    fn_name = fn.__qualname__
    inputs = r.lrange(f"{fn_name}:inputs", 0, -1)
    outputs = r.lrange(f"{fn_name}:outputs", 0, -1)
    call_count = len(inputs)

    print(f"{fn_name} was called {call_count} times:")
    for i, o in zip(inputs, outputs):
        print(f"{fn_name}{i.decode('utf-8')} -> {o.decode('utf-8')}")
