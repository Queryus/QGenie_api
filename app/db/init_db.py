# db/init_db.py
import logging
import sqlite3

from app.core.utils import get_db_path


def _synchronize_table(cursor, table_name: str, target_columns: dict):
    """
    테이블 스키마를 확인하고, 코드와 다를 경우 테이블을 재생성하여 동기화합니다.
    """
    try:
        # 외래 키 제약 조건 비활성화
        cursor.execute("PRAGMA foreign_keys=off;")
        cursor.execute(f"PRAGMA table_info({table_name})")
        current_schema_rows = cursor.fetchall()
        current_columns = {row[1]: row[2].upper() for row in current_schema_rows}

        target_schema_simple = {
            name: definition.split()[0].upper()
            for name, definition in target_columns.items()
            if not name.startswith("FOREIGN KEY")
        }

        if current_columns == target_schema_simple:
            # 외래 키 제약 조건 다시 활성화
            cursor.execute("PRAGMA foreign_keys=on;")
            return

        logging.warning(
            f"'{table_name}' 테이블의 스키마 변경을 감지했습니다. 마이그레이션을 시작합니다. (데이터 손실 위험)"
        )

        temp_table_name = f"{table_name}_temp_old"
        cursor.execute(f"DROP TABLE IF EXISTS {temp_table_name}")  # DROP 먼저 실행
        cursor.execute(f"ALTER TABLE {table_name} RENAME TO {temp_table_name}")

        columns_with_definitions = ", ".join([f"{name} {definition}" for name, definition in target_columns.items()])
        cursor.execute(f"CREATE TABLE {table_name} ({columns_with_definitions})")

        cursor.execute(f"PRAGMA table_info({temp_table_name})")
        temp_columns = {row[1] for row in cursor.fetchall()}
        common_columns = ", ".join(target_columns.keys() & temp_columns)

        if common_columns:
            cursor.execute(
                f"INSERT INTO {table_name} ({common_columns}) SELECT {common_columns} FROM {temp_table_name}"
            )
            logging.info(f"'{temp_table_name}'에서 '{table_name}'으로 데이터를 복사했습니다.")

        cursor.execute(f"DROP TABLE {temp_table_name}")
        logging.info(f"임시 테이블 '{temp_table_name}'을(를) 삭제했습니다.")

    except sqlite3.Error as e:
        logging.error(f"'{table_name}' 테이블 마이그레이션 중 오류 발생: {e}")
        raise e
    finally:
        # 외래 키 제약 조건 다시 활성화
        cursor.execute("PRAGMA foreign_keys=on;")


def initialize_database():
    """
    데이터베이스에 연결하고, 테이블 스키마를 최신 상태로 동기화합니다.
    """
    db_path = get_db_path()
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("BEGIN")
        cursor = conn.cursor()

        # --- db_profile 테이블 처리 ---
        db_profile_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "type": "VARCHAR(32) NOT NULL",
            "host": "VARCHAR(255)",
            "port": "INTEGER",
            "name": "VARCHAR(64)",
            "username": "VARCHAR(128)",
            "password": "VARCHAR(128)",
            "view_name": "VARCHAR(64)",
            "annotation_id": "VARCHAR(64)",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (annotation_id)": "REFERENCES database_annotation(id) ON DELETE SET NULL",
        }
        create_sql = (
            f"CREATE TABLE IF NOT EXISTS db_profile ({', '.join([f'{k} {v}' for k, v in db_profile_cols.items()])})"
        )
        cursor.execute(create_sql)
        _synchronize_table(
            cursor, "db_profile", {k: v for k, v in db_profile_cols.items() if not k.startswith("FOREIGN KEY")}
        )

        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_db_profile_updated_at
            BEFORE UPDATE ON db_profile FOR EACH ROW
            BEGIN UPDATE db_profile SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- ai_credential 테이블 처리 ---
        ai_credential_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "service_name": "VARCHAR(32) NOT NULL UNIQUE",
            "api_key": "VARCHAR(256) NOT NULL",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        }
        create_sql = f"CREATE TABLE IF NOT EXISTS ai_credential ({', '.join([f'{k} {v}' for k, v in ai_credential_cols.items()])})"
        cursor.execute(create_sql)
        _synchronize_table(cursor, "ai_credential", ai_credential_cols)

        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_ai_credential_updated_at
            BEFORE UPDATE ON ai_credential FOR EACH ROW
            BEGIN UPDATE ai_credential SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- chat_tab 테이블 처리 ---
        chat_tab_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "name": "VARCHAR(128)",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        }
        create_sql = (
            f"CREATE TABLE IF NOT EXISTS chat_tab ({', '.join([f'{k} {v}' for k, v in chat_tab_cols.items()])})"
        )
        cursor.execute(create_sql)
        _synchronize_table(cursor, "chat_tab", chat_tab_cols)
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_chat_tab_updated_at
            BEFORE UPDATE ON chat_tab FOR EACH ROW
            BEGIN UPDATE chat_tab SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- chat_message 테이블 처리 ---
        chat_message_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "chat_tab_id": "VARCHAR(64) NOT NULL",
            "sender": "VARCHAR(1) NOT NULL",
            "message": "TEXT NOT NULL",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (chat_tab_id)": "REFERENCES chat_tab(id) ON DELETE CASCADE",
        }
        create_sql = (
            f"CREATE TABLE IF NOT EXISTS chat_message ({', '.join([f'{k} {v}' for k, v in chat_message_cols.items()])})"
        )
        cursor.execute(create_sql)
        _synchronize_table(
            cursor, "chat_message", {k: v for k, v in chat_message_cols.items() if not k.startswith("FOREIGN KEY")}
        )

        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_chat_message_updated_at
            BEFORE UPDATE ON chat_message FOR EACH ROW
            BEGIN UPDATE chat_message SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- query_history 테이블 처리 ---
        query_history_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "chat_message_id": "VARCHAR(64) NOT NULL",
            "query_text": "TEXT NOT NULL",
            "is_success": "VARCHAR(1) NOT NULL",
            "error_message": "TEXT NOT NULL",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (chat_message_id)": "REFERENCES chat_message(id) ON DELETE CASCADE",
        }
        create_sql = f"CREATE TABLE IF NOT EXISTS query_history ({', '.join([f'{k} {v}' for k, v in query_history_cols.items()])})"
        cursor.execute(create_sql)
        _synchronize_table(
            cursor, "query_history", {k: v for k, v in query_history_cols.items() if not k.startswith("FOREIGN KEY")}
        )

        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_query_history_updated_at
            BEFORE UPDATE ON query_history FOR EACH ROW
            BEGIN UPDATE query_history SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- database_annotation 테이블 처리 ---
        database_annotation_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "db_profile_id": "VARCHAR(64) NOT NULL",
            "database_name": "VARCHAR(255) NOT NULL",
            "description": "TEXT",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (db_profile_id)": "REFERENCES db_profile(id) ON DELETE CASCADE",
        }
        create_sql = f"CREATE TABLE IF NOT EXISTS database_annotation ({', '.join([f'{k} {v}' for k, v in database_annotation_cols.items()])})"
        cursor.execute(create_sql)
        _synchronize_table(
            cursor,
            "database_annotation",
            {k: v for k, v in database_annotation_cols.items() if not k.startswith("FOREIGN KEY")},
        )
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_database_annotation_updated_at
            BEFORE UPDATE ON database_annotation FOR EACH ROW
            BEGIN UPDATE database_annotation SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- table_annotation 테이블 처리 ---
        table_annotation_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "database_annotation_id": "VARCHAR(64) NOT NULL",
            "table_name": "VARCHAR(255) NOT NULL",
            "description": "TEXT",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (database_annotation_id)": "REFERENCES database_annotation(id) ON DELETE CASCADE",
        }
        create_sql = f"CREATE TABLE IF NOT EXISTS table_annotation ({', '.join([f'{k} {v}' for k, v in table_annotation_cols.items()])})"
        cursor.execute(create_sql)
        _synchronize_table(
            cursor,
            "table_annotation",
            {k: v for k, v in table_annotation_cols.items() if not k.startswith("FOREIGN KEY")},
        )
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_table_annotation_updated_at
            BEFORE UPDATE ON table_annotation FOR EACH ROW
            BEGIN UPDATE table_annotation SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- column_annotation 테이블 처리 ---
        column_annotation_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "table_annotation_id": "VARCHAR(64) NOT NULL",
            "column_name": "VARCHAR(255) NOT NULL",
            "data_type": "VARCHAR(64)",
            "is_nullable": "INTEGER NOT NULL DEFAULT 1",
            "default_value": "TEXT",
            "check_expression": "TEXT",
            "ordinal_position": "INTEGER",
            "description": "TEXT",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (table_annotation_id)": "REFERENCES table_annotation(id) ON DELETE CASCADE",
        }
        create_sql = f"CREATE TABLE IF NOT EXISTS column_annotation ({', '.join([f'{k} {v}' for k, v in column_annotation_cols.items()])})"
        cursor.execute(create_sql)
        _synchronize_table(
            cursor,
            "column_annotation",
            {k: v for k, v in column_annotation_cols.items() if not k.startswith("FOREIGN KEY")},
        )
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_column_annotation_updated_at
            BEFORE UPDATE ON column_annotation FOR EACH ROW
            BEGIN UPDATE column_annotation SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- table_relationship 테이블 처리 ---
        table_relationship_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "database_annotation_id": "VARCHAR(64) NOT NULL",
            "from_table_id": "VARCHAR(64) NOT NULL",
            "to_table_id": "VARCHAR(64) NOT NULL",
            "relationship_type": "VARCHAR(32) NOT NULL",
            "description": "TEXT",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (database_annotation_id)": "REFERENCES database_annotation(id) ON DELETE CASCADE",
            "FOREIGN KEY (from_table_id)": "REFERENCES table_annotation(id) ON DELETE CASCADE",
            "FOREIGN KEY (to_table_id)": "REFERENCES table_annotation(id) ON DELETE CASCADE",
        }
        create_sql = f"CREATE TABLE IF NOT EXISTS table_relationship ({', '.join([f'{k} {v}' for k, v in table_relationship_cols.items()])})"
        cursor.execute(create_sql)
        _synchronize_table(
            cursor,
            "table_relationship",
            {k: v for k, v in table_relationship_cols.items() if not k.startswith("FOREIGN KEY")},
        )
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_table_relationship_updated_at
            BEFORE UPDATE ON table_relationship FOR EACH ROW
            BEGIN UPDATE table_relationship SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- table_constraint 테이블 처리 ---
        table_constraint_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "table_annotation_id": "VARCHAR(64) NOT NULL",
            "constraint_type": "VARCHAR(16) NOT NULL",
            "name": "VARCHAR(255)",
            "description": "TEXT",
            "expression": "TEXT",
            "ref_table": "VARCHAR(255)",
            "on_update_action": "VARCHAR(16)",
            "on_delete_action": "VARCHAR(16)",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (table_annotation_id)": "REFERENCES table_annotation(id) ON DELETE CASCADE",
        }
        create_sql = f"CREATE TABLE IF NOT EXISTS table_constraint ({', '.join([f'{k} {v}' for k, v in table_constraint_cols.items()])})"
        cursor.execute(create_sql)
        _synchronize_table(
            cursor,
            "table_constraint",
            {k: v for k, v in table_constraint_cols.items() if not k.startswith("FOREIGN KEY")},
        )
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_table_constraint_updated_at
            BEFORE UPDATE ON table_constraint FOR EACH ROW
            BEGIN UPDATE table_constraint SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- constraint_column 테이블 처리 ---
        constraint_column_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "constraint_id": "VARCHAR(64) NOT NULL",
            "column_annotation_id": "VARCHAR(64) NOT NULL",
            "position": "INTEGER",
            "referenced_column_name": "VARCHAR(255)",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (constraint_id)": "REFERENCES table_constraint(id) ON DELETE CASCADE",
            "FOREIGN KEY (column_annotation_id)": "REFERENCES column_annotation(id) ON DELETE CASCADE",
        }
        create_sql = f"CREATE TABLE IF NOT EXISTS constraint_column ({', '.join([f'{k} {v}' for k, v in constraint_column_cols.items()])})"
        cursor.execute(create_sql)
        _synchronize_table(
            cursor,
            "constraint_column",
            {k: v for k, v in constraint_column_cols.items() if not k.startswith("FOREIGN KEY")},
        )
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_constraint_column_updated_at
            BEFORE UPDATE ON constraint_column FOR EACH ROW
            BEGIN UPDATE constraint_column SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- index_annotation 테이블 처리 ---
        index_annotation_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "table_annotation_id": "VARCHAR(64) NOT NULL",
            "name": "VARCHAR(255)",
            "is_unique": "INTEGER NOT NULL DEFAULT 0",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (table_annotation_id)": "REFERENCES table_annotation(id) ON DELETE CASCADE",
        }
        create_sql = f"CREATE TABLE IF NOT EXISTS index_annotation ({', '.join([f'{k} {v}' for k, v in index_annotation_cols.items()])})"
        cursor.execute(create_sql)
        _synchronize_table(
            cursor,
            "index_annotation",
            {k: v for k, v in index_annotation_cols.items() if not k.startswith("FOREIGN KEY")},
        )
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_index_annotation_updated_at
            BEFORE UPDATE ON index_annotation FOR EACH ROW
            BEGIN UPDATE index_annotation SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        # --- index_column 테이블 처리 ---
        index_column_cols = {
            "id": "VARCHAR(64) PRIMARY KEY NOT NULL",
            "index_id": "VARCHAR(64) NOT NULL",
            "column_annotation_id": "VARCHAR(64) NOT NULL",
            "position": "INTEGER",
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (index_id)": "REFERENCES index_annotation(id) ON DELETE CASCADE",
            "FOREIGN KEY (column_annotation_id)": "REFERENCES column_annotation(id) ON DELETE CASCADE",
        }
        create_sql = (
            f"CREATE TABLE IF NOT EXISTS index_column ({', '.join([f'{k} {v}' for k, v in index_column_cols.items()])})"
        )
        cursor.execute(create_sql)
        _synchronize_table(
            cursor, "index_column", {k: v for k, v in index_column_cols.items() if not k.startswith("FOREIGN KEY")}
        )
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_index_column_updated_at
            BEFORE UPDATE ON index_column FOR EACH ROW
            BEGIN UPDATE index_column SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
            """
        )

        conn.commit()

    except sqlite3.Error as e:
        logging.error(f"데이터베이스 초기화 중 오류 발생: {e}. 변경 사항을 롤백합니다.")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
