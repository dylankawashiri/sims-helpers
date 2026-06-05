from __future__ import annotations

import os

class Report:
    def __init__(self, name: str | os.PathLike[str], dir: str | os.PathLike[str] | None = None):
        raise NotImplementedError()