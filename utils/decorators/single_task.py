import functools
from django.core.cache import cache


def single_task(timeout):
    def task_exc(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_id = "celery_single_task_" + func.__name__
            acquire_lock = lambda: cache.add(lock_id, "true", timeout)
            release_lock = lambda: cache.delete(lock_id)
            result = -1
            if acquire_lock():
                try:
                    result = func(*args, **kwargs)
                finally:
                    release_lock()
            return result

        return wrapper

    return task_exc
