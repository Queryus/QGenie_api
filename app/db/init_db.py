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
        # ConnectionProfile 테이블 생성
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ConnectionProfile (
            id INTEGER PRIMARY KEY,
            db_type TEXT NOT NULL,
            host TEXT NOT NULL,
            port INTEGER NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ConnectionProfile에 updated_at 자동 갱신을 위한 트리거 생성
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_connectionprofile_updated_at
        AFTER UPDATE ON ConnectionProfile
        FOR EACH ROW
        BEGIN
            UPDATE ConnectionProfile SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
        END;
        """)

        # APICredential 테이블 생성
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS APICredential (
            id INTEGER PRIMARY KEY,
            service_name TEXT NOT NULL,
            api_key TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # APICredential에 updated_at 자동 갱신을 위한 트리거 생성
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_apicredential_updated_at
        AFTER UPDATE ON APICredential
        FOR EACH ROW
        BEGIN
            UPDATE APICredential SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
        END;
        """)

        conn.commit()

    except sqlite3.Error as e:
        print(f"데이터베이스 초기화 중 오류 발생: {e}")
    finally:
        if conn:
            conn.close()

