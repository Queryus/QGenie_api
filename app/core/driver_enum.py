# app/assets/driver_enum.py
from enum import Enum


class DriverEnum(Enum):
    """지원되는 데이터베이스 드라이버 타입"""

    postgresql = ("postgresql", "psycopg2")
    mysql = ("mysql", "mysql.connector")
    sqlite = ("sqlite", "sqlite3")
    oracle = ("oracle", "cx_Oracle")
    sqlserver = ("sqlserver", "pyodbc")
    mariadb = ("mariadb", "pymysql")

    def __init__(self, db_type, driver_module):
        self.db_type = db_type
        self.driver_module = driver_module

    def __str__(self):
        return self.db_type
