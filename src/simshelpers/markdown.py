from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class Markdown:
    def __init__(self, name: str | os.PathLike[str], dir: str | os.PathLike[str] | None = None):
        name = name
        dir = dir if dir is not None else Path(__file__).resolve().parent.parent.parent / "reports"
        self.save_path = Path(f"{dir}/{name}.md").expanduser()

        self.contents: list[str] = []
        self.text_options: dict[str, str] = {f"h{k}": "#" * k for k in range(1, 7)}
        self.text_options["p"] = ""


    def save(self):
        """Save markdown file."""
        if self.contents:
            with open(self.save_path, "w") as f:
                for line in self.contents:
                    f.write(line)
            print(f"Markdown file saved to: {self.save_path}")
        else:
            raise RuntimeError("Content of markdown file is empty!")


    def add_text(self, message: str, text_type: str| int = "p", *, endline: bool = True) -> None:
        """
        Add text to markdown file.
        
        Args:
            message (str): Message to add.
            text_type (str, optional): Text type (h1, h2, h3, ..., h6, p. Defaults to p.
            endline (bool, optional): True if you want to return after input. Defaults to True.
        """
        if type(text_type) is not str:
            text_type = f"h{text_type}"
        if endline:
            message += "\n"
        if text_type.lower() in self.text_options.keys():
            self.contents.append(f"{self.text_options[text_type]} {message}")
        else:
            raise TypeError(f"Type of {text_type} not an option, please select one of:\n{self.text_options.keys()}")


    def add_table(self, table: dict[Any, list[int]] | dict[Any, list[float]] |dict[Any, list[bool]] |dict[Any, list[str]]):
        """
        Add a table to a markdown file.
        
        Args:
            table (dict): Table.
        """
        header = ""
        header_close = ""
        for key in table.keys():
            header += f"| {key} "
            header_close += "| --- "
        header += "|"
        header_close += "|"
        lines: list[str] = []
        max_length = max(len(v) for v in table.values())
        for i in range(max_length):
            line = ""
            for key in table.keys():
                if i >= len(table[key]):
                    line += "| NaN"
                else:
                    line += f"| {table[key][i]}"
            line += "|"
            lines.append(line)
        self.add_text("\n")
        self.add_text(header)
        self.add_text(header_close)
        for line in lines:
            self.add_text(line)


    def add_divider(self):
        self.add_text("---")
