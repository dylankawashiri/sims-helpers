from collections.abc import Iterable
from functools import partial
import multiprocessing
from typing import Any, Callable


def parallel_map(func: Callable[[Any], Any], param_range: Iterable[Any], *, processes: int | None = None, **kwargs: Any):
    if __name__ != "__main__":
        multiprocessing.freeze_support()
    function = func if not kwargs else partial(func, **kwargs)
    
    p = multiprocessing.Pool(processes)
    try:
        results = p.map_async(function, param_range)
        results = results.get()
    except KeyboardInterrupt:
        p.terminate()
        p.join()
        raise
    finally:
        try:
             p.close()
        except Exception:
             pass
        p.join()
    return results
