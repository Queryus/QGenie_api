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

        # column_annotation 테이블 생성 (단일 컬럼 스펙 전용)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS column_annotation (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                table_annotation_id VARCHAR(64) NOT NULL,
                column_name VARCHAR(255) NOT NULL,
                -- 데이터 타입 (원본 DB의 타입 문자열을 그대로 저장; 예: BIGINT, TEXT, TIMESTAMP)
                data_type VARCHAR(64),
                -- NULL 허용 여부 (1:true, 0:false)
                is_nullable INTEGER NOT NULL DEFAULT 1,
                -- 기본값(리터럴 또는 표현식; 문자열 형태로 저장)
                default_value TEXT,
                -- 단일 컬럼 기준 CHECK 제약 표현(예: "value > 0")
                check_expression TEXT,
                -- 컬럼 순서
                ordinal_position INTEGER,
                -- 설명
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

        # ---------------------------------------------------------------------
        # 복합 제약(Primary/Unique/ForeignKey/Check) 메타데이터 테이블 생성
        #  - 여러 컬럼을 묶는 제약을 '그룹' 단위로 관리
        #  - UI 배지/목록은 이 테이블들에서 파생 계산
        # ---------------------------------------------------------------------

        # table_constraint 테이블 생성 (제약 그룹 본체)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS table_constraint (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                table_annotation_id VARCHAR(64) NOT NULL,
                -- PRIMARY_KEY | UNIQUE | FOREIGN_KEY | CHECK
                constraint_type VARCHAR(16) NOT NULL,
                -- DB 제약명(선택)
                name VARCHAR(255),
                -- CHECK 제약식 등 (FK/PK/UNIQUE에는 NULL 가능)
                expression TEXT,
                -- FOREIGN KEY 전용: 참조 테이블명
                ref_table VARCHAR(255),
                -- FOREIGN KEY 전용: 액션
                on_update_action VARCHAR(16),
                on_delete_action VARCHAR(16),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_annotation_id) REFERENCES table_annotation(id) ON DELETE CASCADE
            );
            """
        )
        # table_constraint 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_table_constraint_updated_at
            BEFORE UPDATE ON table_constraint
            FOR EACH ROW
            BEGIN
                UPDATE table_constraint SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        )

        # constraint_column 테이블 생성 (제약 그룹 ↔ 컬럼 매핑)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS constraint_column (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                constraint_id VARCHAR(64) NOT NULL,
                column_annotation_id VARCHAR(64) NOT NULL,
                -- 복합 제약 내 컬럼 순서(1, 2, 3, ...)
                position INTEGER,
                -- FOREIGN KEY 전용: 참조 테이블의 대응 컬럼명 (복합 FK 매핑)
                referenced_column_name VARCHAR(255),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (constraint_id) REFERENCES table_constraint(id) ON DELETE CASCADE,
                FOREIGN KEY (column_annotation_id) REFERENCES column_annotation(id) ON DELETE CASCADE
            );
            """
        )
        # constraint_column 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_constraint_column_updated_at
            BEFORE UPDATE ON constraint_column
            FOR EACH ROW
            BEGIN
                UPDATE constraint_column SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        )

        # ---------------------------------------------------------------------
        # 인덱스(복합 포함) 메타데이터 테이블 생성
        #  - DB 인덱스명을 보존하고, 컬럼 순서를 기록
        # ---------------------------------------------------------------------

        # index_annotation 테이블 생성 (인덱스 그룹 본체)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS index_annotation (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                table_annotation_id VARCHAR(64) NOT NULL,
                name VARCHAR(255),                -- DB 인덱스명(선택)
                is_unique INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_annotation_id) REFERENCES table_annotation(id) ON DELETE CASCADE
            );
            """
        )
        # index_annotation 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_index_annotation_updated_at
            BEFORE UPDATE ON index_annotation
            FOR EACH ROW
            BEGIN
                UPDATE index_annotation SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        )

        # index_column 테이블 생성 (인덱스 그룹 ↔ 컬럼 매핑)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS index_column (
                id VARCHAR(64) PRIMARY KEY NOT NULL,
                index_id VARCHAR(64) NOT NULL,
                column_annotation_id VARCHAR(64) NOT NULL,
                -- 인덱스 내 컬럼 순서(1, 2, 3, ...)
                position INTEGER,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (index_id) REFERENCES index_annotation(id) ON DELETE CASCADE,
                FOREIGN KEY (column_annotation_id) REFERENCES column_annotation(id) ON DELETE CASCADE
            );
            """
        )
        # index_column 테이블의 updated_at을 자동으로 업데이트하는 트리거
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_index_column_updated_at
            BEFORE UPDATE ON index_column
            FOR EACH ROW
            BEGIN
                UPDATE index_column SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        )

        conn.commit()

    except sqlite3.Error as e:
        print(f"데이터베이스 초기화 중 오류 발생: {e}")
    finally:
        if conn:
            conn.close()
