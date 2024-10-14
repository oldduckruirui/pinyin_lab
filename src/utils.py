import time
import logging


def metric(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logging.info('<{}.{}> took {:.2f}s'.format(
            func.__module__, func.__name__, end - start))
        return result
    return wrapper
