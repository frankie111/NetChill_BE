import json
from datetime import timedelta, datetime
from functools import wraps

import redis

rd = redis.Redis(host="localhost", port=6379, db=0)

POPULAR_MOVIES_CACHE_SUFFIX = "_popular_movies"


def merge_args_and_kwargs(*args, **kwargs):
    merged = [a for a in args if isinstance(a, str)]

    for value in kwargs.values():
        if isinstance(value, str):
            merged.append(value)

    return merged


def redis(cache_duration: timedelta, suffix: str = None, ignore_cache: bool = False):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            # Determine if function is a method of a class
            tmp = merge_args_and_kwargs(*args, **kwargs)
            is_method = False
            if len(tmp) > 1 and isinstance(tmp[0], object):
                is_method = True

            query = "_".join(tmp)

            key = query
            if suffix:
                key += suffix

            if not ignore_cache:
                try:
                    cached_data = rd.get(key)
                    if cached_data is not None:
                        print(key, "data found in cache")
                        result = json.loads(cached_data)
                        # dont return empty results
                        if len(result) > 0:
                            return result
                except Exception as e:
                    print(f"Error while fetching data from Redis cache: {e}")
            else:
                print("Ignoring cache")

            # Call the original function with appropriate arguments
            result = function(*args, **kwargs)

            # dont cache empty results
            if result is None:
                return result

            # check if bool
            if isinstance(result, bool):
                return result

            # dont cache empty results
            if len(result) == 0:
                return result

            try:
                rd.setex(key, cache_duration, json.dumps(result))
                print(key, "data cached successfully")
            except Exception as e:
                print(f"Error while caching data in Redis: {e}")

            return result

        return wrapper

    return decorator


def async_redis(cache_duration: timedelta, suffix: str = None, ignore_cache: bool = False):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            # Determine if function is a method of a class
            tmp = merge_args_and_kwargs(*args, **kwargs)
            is_method = False
            if len(tmp) > 1 and isinstance(tmp[0], object):
                is_method = True

            query = "_".join(tmp)

            key = query
            if suffix:
                key += suffix

            if not ignore_cache:
                try:
                    cached_data = await rd.get(key)
                    if cached_data is not None:
                        print(key, "data found in cache")
                        result = json.loads(cached_data)
                        # dont return empty results
                        if len(result) > 0:
                            return result
                except Exception as e:
                    print(f"Error while fetching data from Redis cache: {e}")
            else:
                print("Ignoring cache")

            # Call the original function with appropriate arguments
            result = await function(*args, **kwargs)

            # dont cache empty results
            if result is None:
                return result

            # check if bool
            if isinstance(result, bool):
                return result

            # dont cache empty results
            if len(result) == 0:
                return result

            try:
                await rd.setex(key, cache_duration, json.dumps(result))
                print(key, "data cached successfully")
            except Exception as e:
                print(f"Error while caching data in Redis: {e}")

            return result

        return wrapper

    return decorator


def delete(key: str, suffix: str = ""):
    key = key + suffix
    if rd.exists(key):
        print(f"Deleting cache key: {key}")
        rd.delete(key)
    else:
        print(f"Cache key not found: {key}")
