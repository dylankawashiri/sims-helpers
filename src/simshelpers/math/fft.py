import importlib
from typing import Any

library = None


def make_cupy_default():
    global library, module
    library = "cupyx.scipy"
    module = importlib.import_module(library)


_fft = getattr(module, "fft")
_ifft = getattr(module, "ifft")
_fft2 = getattr(module, "fftshift")
_ifft2 = getattr(module, "ifftshift")


def fft(*args: Any, **kwargs: Any):
    return _fft(args, kwargs)

def ifft(*args: Any, **kwargs: Any):
    return _ifft(args, kwargs)

