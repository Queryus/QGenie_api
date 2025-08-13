# app/core/enum/db_key_prefix_name.py
from enum import Enum


class DBSaveIdEnum(Enum):
    """저장할 디비 ID 앞에 들어갈 이름"""

    user_db = "USER-DB"
    driver = "DRIVER"
    api_key = "API-KEY"
    chat_tab = "CHAT_TAB"

    database_annotation = "DB-ANNO"
    table_annotation = "TBL-ANNO"
    column_annotation = "COL-ANNO"
