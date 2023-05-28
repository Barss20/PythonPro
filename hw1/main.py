import requests
import tracemalloc
from collections import OrderedDict
import functools
from colorama import Fore, Style


def format_memory_size(size):
    units = ['B', 'KB', 'MB', 'GB']
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"


def memory_usage(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = f(*args, **kwargs)
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        print(f"{Fore.BLUE}[ Top 10 Memory Usage ]")
        for index, stat in enumerate(top_stats[:10], start=1):
            size = format_memory_size(stat.size)
            traceback = stat.traceback
            frame = traceback[0]
            filename = frame.filename
            lineno = frame.lineno
            if index == 1:
                print(f"{Fore.RED}{index}. File: {filename}, Line: {lineno}, Memory: {size}{Style.RESET_ALL}")
            else:
                print(f"{index}. File: {filename}, Line: {lineno}, Memory: {size}")

        tracemalloc.stop()
        return result

    return wrapper


def cache(max_limit=64):
    def internal(f):
        @functools.wraps(f)
        def decorator(*args, **kwargs):
            cache_key = (args, tuple(kwargs.items()))
            if cache_key in decorator._cache:
                decorator._cache.move_to_end(cache_key, last=True)
                return decorator._cache[cache_key]
            result = f(*args, **kwargs)
            if len(decorator._cache) > max_limit:
                key_to_drop = min(decorator._cache, key=decorator._cache_counter.get)
                decorator._cache.pop(key_to_drop)
                decorator._cache_counter.pop(key_to_drop)
            decorator._cache[cache_key] = result
            decorator._cache_counter[cache_key] = 1
            return result

        decorator._cache = OrderedDict()
        decorator._cache_counter = {}
        return decorator

    return internal


@memory_usage
@cache(max_limit=10)
def fetch_url(url, first_n=100):
    """Fetch a given url"""
    res = requests.get(url)
    return res.content[:first_n] if first_n else res.content


# Приклад використання
content1 = fetch_url('https://google.com', first_n=50)
print(f"[Content 1]\n{content1}")

content2 = fetch_url('https://google.com', first_n=50)
print(f"[Content 2]\n{content2}")

content3 = fetch_url('https://google.com', first_n=200)
print(f"[Content 3]\n{content3}")

content4 = fetch_url('https://google.com', first_n=50)
print(f"[Content 4]\n{content4}")