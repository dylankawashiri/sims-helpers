from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import mariadb # type: ignore
import numpy as np
import pandas as pd
import yaml


class Database:
    def __init__(self, creds_file: str | Path = Path("creds.yaml"), dir: str | Path | None = None):
        if not dir:
            dir = Path(__file__).resolve().parent.parent / "database/credentials"
        
        with open(fr"{dir}/{creds_file}", "r") as f:
            db_config = yaml.safe_load(f)["config"]

        self.conn =  mariadb.connect(**db_config)
        self.cursor = self.conn.cursor()
        self._database: str | None = None
        self.databases: list[str] | None = None

    def execute(self, msg: str, params: Sequence[Any] | None = None) -> Any:
        return self.cursor.execute(msg, params)
    
    def commit(self):
        self.conn.commit()
    
    def version(self) -> str:
        self.execute("SELECT VERSION();")
        row = self.cursor.fetchone()[0]
        return row

    def current_database(self):
        return self._database
  
    def list_databases(self, *, to_print: bool = False) -> list[str]:
        self.execute("SHOW DATABASES")
        self.databases = [db[0] for db in self.cursor]
        if to_print:
            print(f"Available databases: {self.databases}")
        return self.databases

    def list_tables(self, *, to_print: bool = False) -> list[str]:
        self.execute("SHOW TABLES")
        self.tables = [tbl[0] for tbl in self.cursor]
        if to_print:
            print(f"Tables available in database '{self._database}': {self.tables}")
        return self.tables

    def set_database(self, db: str):
        self.create_database(db)
        self.execute(f"USE {db}")
        self._database = db

    def create_database(self, db: str):
        self.execute(f"CREATE DATABASE IF NOT EXISTS {db}")

      # should redo with tuples
    def create_new_table(self, table_name: str, *, table: dict[Any, Any] | pd.DataFrame, del_if_exists: bool = True):
        if del_if_exists:
            self.execute(f"DROP TABLE IF EXISTS {table_name}")
        if type(table) is pd.DataFrame:
            table = table.to_dict(orient="list")
        type_dict: dict[Any, str | None] = {k: None for k in table.keys()}
        for item in table:
            if isinstance(table[item], (Sequence, Iterable)):
                if isinstance(table[item], np.ndarray):
                    table[item] = table[item].tolist()
                to_check = next((x for x in table[item] if x is not None), None)
            else:
                to_check = table[item]
            if to_check is None:
                type_dict[item] = "TEXT"
            elif isinstance(to_check, float):
                type_dict[item] = "FLOAT"
            elif isinstance(to_check, int):
                type_dict[item] = "INT"
            elif type(to_check) is bool:
                type_dict[item] = "BOOL"
            elif type(to_check) is str:
                type_dict[item] = "TEXT"
            else:
                raise TypeError(f"Not a supported type: {type(to_check)}")
        msg = f"CREATE TABLE {table_name} (\n"

        len_dict = len(type_dict.keys())

        for idx, key in enumerate(type_dict):
            msg += f"{key}   {type_dict[key]}"
            if idx < len_dict - 1:
                msg += ",\n"
            else:
                msg += ")"
        self.execute(msg)
        self.add_to_table(table_name, table=table)

    def add_to_table(self, table_name: str, *, table: dict[Any, Any] | pd.DataFrame):
        max_len = len(table[max(table, key=lambda k: len(table[k]))])
        val = []
        len_dict = {key: len(table[key]) for key in table}
        for i in range(max_len):
            add_tuple = ()
            for key in table:
                if i < len_dict[key]:
                    row_value = table[key][i]
                    if pd.isna(row_value):
                        row_value = None
                else:
                    row_value = None
                add_tuple += (row_value,)
            val.append(add_tuple)
        placeholders = ",".join(["?" for _ in table])
        for i in range(max_len):
            msg = f"INSERT INTO {table_name} VALUES ({placeholders})"
            self.execute(msg, val[i])
        self.commit()
    
    def select_from_table(self, table_name: str, *args: str, use_pandas: bool = True) -> dict[Any, Any] | pd.DataFrame:
        """Get data from a table."""
        values = ""
        if not args:
            values += "*"
        else:
            for idx, arg in enumerate(args):
                if idx < len(args) -1:
                    values += f"{arg} "
        query = f"SELECT {values} FROM {table_name}"
        if use_pandas:
            return pd.read_sql(query, con=self.conn)
        self.execute(query)
        values = self.cursor.fetchall()
        # values = [value[0] for value in values]
        return values
    
    def disconnect(self) -> None:
        self.cursor.close()
        self.conn.close()

def to_database(data: dict[Any, Any] | pd.DataFrame, creds_file: str | Path = Path("creds.yaml"), dir: str | Path | None = None, db_name: str = "database_default", table_name: str = "table_default"):
    database = Database(creds_file, dir)
    database.set_database(db_name)
    database.create_new_table(table_name, table = data)
