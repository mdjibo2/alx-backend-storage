#!/usr/bin/env python3
"""Cache class for storing data in Redis."""

import uuid
import redis
from typing import Union
from typing import Callable
import functools

class Cache:

    def __init__(self):
        """Initialize Redis client and flush Redis database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis using a random key.

        Args:
            data (Union[str, bytes, int, float]): Data to be stored.

        Returns:
            str: Random key used to store the data in Redis.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable[[bytes], any] = None) -> Union[bytes, any]:
        """
        Retrieve the data stored at the given key in Redis.

        Args:
            key: The key of the data to retrieve from Redis.
            fn: An optional function to convert the retrieved data to a different type.

        Returns:
            The retrieved data as bytes if fn is None, or the result of applying fn to the retrieved data.
            Returns None if the key is not found in Redis.
        """

        data = self._redis.get(key)
        if data is None:
            return data
        if fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
         """
        Retrieve the data stored at the given key in Redis as a UTF-8 string.

        Args:
            key: The key of the data to retrieve from Redis.

        Returns:
            The retrieved data as a UTF-8 string.
        """

        return self.get(key, fn=lambda x: x.decode("utf-8"))

    def get_int(self, key: str) -> int:
         """
        Retrieve the data stored at the given key in Redis as an integer.

        Args:
            key: The key of the data to retrieve from Redis.

        Returns:
            The retrieved data as an integer.
        """
        
        return self.get(key, fn=int)

        def count_calls(func: Callable) -> Callable:
        """
        Decorator function that counts the number of times a method is called.

        Args:
            func (Callable): The method to be decorated.

        Returns:
            Callable: The wrapped function that increments the count for that key
            every time the method is called and returns the value returned by the original method.
        """
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            key = func.__qualname__
            self._redis.incr(key)
            return func(self, *args, **kwargs)
        return wrapper

    @count_calls
    def store(self, data: bytes) -> str:
        """
        Method that generates a random key and stores the input data in Redis using the key.

        Args:
            data (bytes): The input data to be stored in Redis.

        Returns:
            str: The randomly generated key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
