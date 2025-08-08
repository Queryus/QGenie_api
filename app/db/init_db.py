# db/init_db.py
import sqlite3

from app.core.utils import get_db_path

"""
데이터베이스에 연결하고, 애플리케이션에 필요한 테이블이 없으면 생성합니다.
"""


def initialize_database():

    db_path = get_db_path()
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # db_profile 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS db_profile (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                type VARCHAR(32) NOT NULL,
                host VARCHAR(255) NOT NULL,
                port INTEGER NOT NULL,
                name VARCHAR(64),
                username VARCHAR(128) NOT NULL,
                password VARCHAR(128) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        # db_profile 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_db_profile_updated_at
            BEFORE UPDATE ON db_profile
            FOR EACH ROW
            BEGIN
                UPDATE db_profile SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """
        )

        # ai_credential 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_credential (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                service_name VARCHAR(32) NOT NULL UNIQUE,
                api_key VARCHAR(256) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        # ai_credential 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_ai_credential_updated_at
            BEFORE UPDATE ON ai_credential
            FOR EACH ROW
            BEGIN
                UPDATE ai_credential SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """
        )

        # chat_tab 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_tab (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                name VARCHAR(128),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        # chat_tab 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_chat_tab_updated_at
            BEFORE UPDATE ON chat_tab
            FOR EACH ROW
            BEGIN
                UPDATE chat_tab SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """
        )

        # chat_message 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_message (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                chat_tab_id VARCHAR(64) NOT NULL,
                sender VARCHAR(1) NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_tab_id) REFERENCES chat_tab(id)
            );
        """
        )
        # chat_message 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_chat_message_updated_at
            BEFORE UPDATE ON chat_message
            FOR EACH ROW
            BEGIN
                UPDATE chat_message SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """
        )

        # query_history 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS query_history (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                chat_message_id VARCHAR(64) NOT NULL,
                query_text TEXT NOT NULL,
                is_success VARCHAR(1) NOT NULL,
                error_message TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_message_id) REFERENCES chat_message(id)
            );
        """
        )
        # query_history 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_query_history_updated_at
            BEFORE UPDATE ON query_history
            FOR EACH ROW
            BEGIN
                UPDATE query_history SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """
        )

        # database_annotation 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS database_annotation (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                db_profile_id VARCHAR(64) NOT NULL,
                database_name VARCHAR(255) NOT NULL,
                description TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (db_profile_id) REFERENCES db_profile(id) ON DELETE CASCADE
            );
            """
        )
        # database_annotation 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_database_annotation_updated_at
            BEFORE UPDATE ON database_annotation
            FOR EACH ROW
            BEGIN
                UPDATE database_annotation SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        )

        # table_annotation 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS table_annotation (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                database_annotation_id VARCHAR(64) NOT NULL,
                table_name VARCHAR(255) NOT NULL,
                description TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (database_annotation_id) REFERENCES database_annotation(id) ON DELETE CASCADE
            );
            """
        )
        # table_annotation 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_table_annotation_updated_at
            BEFORE UPDATE ON table_annotation
            FOR EACH ROW
            BEGIN
                UPDATE table_annotation SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        )

        # column_annotation 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS column_annotation (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                table_annotation_id VARCHAR(64) NOT NULL,
                column_name VARCHAR(255) NOT NULL,
                description TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_annotation_id) REFERENCES table_annotation(id) ON DELETE CASCADE
            );
            """
        )
        # column_annotation 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_column_annotation_updated_at
            BEFORE UPDATE ON column_annotation
            FOR EACH ROW
            BEGIN
                UPDATE column_annotation SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        )

        # table_relationship 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS table_relationship (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                database_annotation_id VARCHAR(64) NOT NULL,
                from_table_id VARCHAR(64) NOT NULL,
                to_table_id VARCHAR(64) NOT NULL,
                relationship_type VARCHAR(32) NOT NULL,
                description TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (database_annotation_id) REFERENCES database_annotation(id) ON DELETE CASCADE,
                FOREIGN KEY (from_table_id) REFERENCES table_annotation(id) ON DELETE CASCADE,
                FOREIGN KEY (to_table_id) REFERENCES table_annotation(id) ON DELETE CASCADE
            );
            """
        )
        # table_relationship 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_table_relationship_updated_at
            BEFORE UPDATE ON table_relationship
            FOR EACH ROW
            BEGIN
                UPDATE table_relationship SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        )

        conn.commit()

    except sqlite3.Error as e:
        print(f"데이터베이스 초기화 중 오류 발생: {e}")
    finally:
        if conn:
            conn.close()
