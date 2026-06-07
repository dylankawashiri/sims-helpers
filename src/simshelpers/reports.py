from __future__ import annotations

import os

from simshelpers.markdown import Markdown

class Report(Markdown):
    def __init__(self, name: str | os.PathLike[str], dir: str | os.PathLike[str] | None = None):
        super().__init__(name, dir)
        
