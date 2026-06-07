from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import mariadb # type: ignore
import numpy as np
import pandas as pd
import yaml

def check_error(func):
    def wrapper(*args: Any, **kwargs: Any) -> Any | None:
        try:
            return func(*args, **kwargs)
        except mariadb.Error as e:
            print(e)
            raise e
    return wrapper

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

    @check_error
    def execute(self, msg: str) -> Any:
        return self.cursor.execute(msg)
    
    @check_error
    def commit(self):
        self.conn.commit()

    @check_error
    def version(self) -> str:
        self.execute("SELECT VERSION();")
        row = self.cursor.fetchone()[0]
        return row
    
    @check_error
    def current_database(self):
        return self._database
    
    @check_error
    def list_databases(self, *, to_print: bool = False) -> list[str]:
        self.execute("SHOW DATABASES")
        self.databases = [db[0] for db in self.cursor]
        if to_print:
            print(f"Available databases: {self.databases}")
        return self.databases
    
    @check_error
    def list_tables(self, *, to_print: bool = False) -> list[str]:
        self.execute("SHOW TABLES")
        self.tables = [tbl[0] for tbl in self.cursor]
        if to_print:
            print(f"Tables available in database '{self._database}': {self.tables}")
        return self.tables

    @check_error
    def set_database(self, db: str):
        self.create_database(db)
        self.execute(f"USE {db}")
        self._database = db

    @check_error
    def create_database(self, db: str):
        self.execute(f"CREATE DATABASE IF NOT EXISTS {db}")

    @check_error  # should redo with tuples
    def create_new_table(self, table_name: str, *, table: dict[Any, Any] | pd.DataFrame, del_if_exists: bool = True):
        if del_if_exists:
            self.execute(f"DROP TABLE IF EXISTS {table_name}")
        if type(table) is pd.DataFrame:
            table = table.to_dict()
        type_dict: dict[Any, str | None] = {k: None for k in table.keys()}
        for item in table:
            if isinstance(table[item], (Sequence, Iterable)):
                if isinstance(table[item], np.ndarray):
                    table[item] = table[item].tolist()
                if not all(type(x) is type(table[item][0]) for x in table[item]):
                    raise TypeError("All elements in a dictionary key must be of the same type!")
                to_check = table[item][0]
            else:
                to_check = table[item]
            if isinstance(to_check, (float)):
                type_dict[item] = "FLOAT(255)"
            elif isinstance(to_check, (int)):
                type_dict[item] = "INT(255)"
            elif type(to_check) is bool:
                type_dict[item] = "BOOL(255)"
            elif type(to_check) is str:
                type_dict[item] = "VARCHAR(255)"
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

    @check_error
    def add_to_table(self, table_name: str, *, table: dict[Any, Any] | pd.DataFrame):
        max_len = len(table[max(table, key=lambda k: len(table[k]))])
        val = []
        len_dict = {key: len(table[key]) for key in table}
        sql_tpl = ()
        for i in range(max_len):
            add_tuple = ()
            for key in table:
                if i < len_dict[key]:
                    add_tuple += (table[key][i], )
                else:
                    add_tuple += ("NULL", )
                if key not in sql_tpl:
                    sql_tpl += (key, )
            val.append(add_tuple)
        for i in range(max_len):
            self.execute(f"INSERT INTO {table_name} VALUES {val[i]}")
        self.commit()

    @check_error
    def select_from_table(self, table_name: str, *args: str, use_pandas: bool = True):
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

    @check_error
    def disconnect(self) -> None:
        self.cursor.close()
        self.conn.close()

# data: dict[Any, Any], table_name: str, db_name: str, 
def to_database(creds_file: str | Path = Path("creds.yaml"), dir: str | Path | None = None):
    database = Database(creds_file, dir)
    print(f"Version: {database.version()}")
    database.set_database("yert")
    database.list_databases(to_print=True)
    database.list_tables(to_print=True)
    table = {
        "data": np.array(range(10)),
        "strings": ["hello", "there"]
    }
    database.create_new_table("data_table", table = table)
    print(database.select_from_table("data_table"))

if __name__ == "__main__":
    to_database()
