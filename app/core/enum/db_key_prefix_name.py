# app/core/enum/db_key_prefix_name.py
from enum import Enum


class DBSaveIdEnum(Enum):
    """저장할 디비 ID 앞에 들어갈 이름"""

    user_db = "USER-DB"
    driver = "DRIVER"
    api_key = "API-KEY"
    chat_tab = "CHAT-TAB"
    query = "QUERY"
    chat_message = "CHAT-MESSAGE"

    database_annotation = "DB-ANNO"
    table_annotation = "TBL-ANNO"
    column_annotation = "COL-ANNO"
    table_constraint = "TC-ANNO"
    constraint_column = "CC-ANNO"
    index_annotation = "IDX-ANNO"
    index_column = "IC-ANNO"
    table_relationship = "TR-ANNO"
