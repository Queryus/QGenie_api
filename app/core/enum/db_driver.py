# app/core/enum/db_driver.py
from enum import Enum


class DBTypesEnum(Enum):
    """지원되는 데이터베이스 드라이버 타입"""

    postgresql = "psycopg2"
    mysql = "mysql.connector"
    sqlite = "sqlite3"
    oracle = "cx_Oracle"
    sqlserver = "pyodbc"
    mariadb = "pymysql"
