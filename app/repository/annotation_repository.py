import sqlite3

from app.core.utils import get_db_path
from app.schemas.annotation.db_model import (
    ColumnAnnotationInDB,
    DatabaseAnnotationInDB,
    TableAnnotationInDB,
)
from app.schemas.annotation.response_model import (
    ColumnAnnotationDetail,
    FullAnnotationResponse,
    TableAnnotationDetail,
)


class AnnotationRepository:
    def create_full_annotation(
        self,
        db_conn: sqlite3.Connection,
        db_annotation: DatabaseAnnotationInDB,
        table_annotations: list[TableAnnotationInDB],
        column_annotations: list[ColumnAnnotationInDB],
        # TODO: Add other annotation types
    ) -> None:
        """
        하나의 트랜잭션 내에서 전체 어노테이션 데이터를 저장합니다.
        - 서비스 계층에서 트랜잭션을 관리하므로 connection을 인자로 받습니다.
        - 실패 시 sqlite3.Error를 발생시킵니다.
        """
        cursor = db_conn.cursor()

        # 1. Database Annotation 저장
        cursor.execute(
            """
            INSERT INTO database_annotation (id, db_profile_id, database_name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                db_annotation.id,
                db_annotation.db_profile_id,
                db_annotation.database_name,
                db_annotation.description,
                db_annotation.created_at,
                db_annotation.updated_at,
            ),
        )

        # 2. Table Annotations 저장 (executemany 사용)
        table_data = [
            (t.id, t.database_annotation_id, t.table_name, t.description, t.created_at, t.updated_at)
            for t in table_annotations
        ]
        cursor.executemany(
            """
            INSERT INTO table_annotation (id, database_annotation_id, table_name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            table_data,
        )

        # 3. Column Annotations 저장 (executemany 사용)
        column_data = [
            (
                c.id,
                c.table_annotation_id,
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.default_value,
                c.check_expression,
                c.ordinal_position,
                c.description,
                c.created_at,
                c.updated_at,
            )
            for c in column_annotations
        ]
        cursor.executemany(
            """
            INSERT INTO column_annotation (id, table_annotation_id, column_name, data_type, is_nullable, default_value, check_expression, ordinal_position, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            column_data,
        )

        # TODO: Constraint, Index 등 나머지 데이터 저장 로직 추가

    def find_full_annotation_by_id(self, annotation_id: str) -> FullAnnotationResponse | None:
        """
        annotationId로 전체 어노테이션 상세 정보를 조회합니다.
        - 여러 테이블을 JOIN하여 구조화된 데이터를 반환합니다.
        - 실패 시 sqlite3.Error를 발생시킵니다.
        """
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 1. 기본 Database Annotation 정보 조회
            cursor.execute("SELECT * FROM database_annotation WHERE id = ?", (annotation_id,))
            db_row = cursor.fetchone()
            if not db_row:
                return None

            # 2. 테이블 및 하위 정보 조회
            cursor.execute("SELECT * FROM table_annotation WHERE database_annotation_id = ?", (annotation_id,))
            table_rows = cursor.fetchall()

            tables_details = []
            for table_row in table_rows:
                table_id = table_row["id"]

                # 컬럼 정보
                cursor.execute(
                    "SELECT id, column_name, description FROM column_annotation WHERE table_annotation_id = ?",
                    (table_id,),
                )
                columns = [ColumnAnnotationDetail.model_validate(dict(c)) for c in cursor.fetchall()]

                # TODO: 제약조건 및 인덱스 정보 조회 로직 추가

                tables_details.append(
                    TableAnnotationDetail(
                        id=table_id,
                        table_name=table_row["table_name"],
                        description=table_row["description"],
                        created_at=table_row["created_at"],
                        updated_at=table_row["updated_at"],
                        columns=columns,
                        constraints=[],  # Placeholder
                        indexes=[],  # Placeholder
                    )
                )

            return FullAnnotationResponse(
                id=db_row["id"],
                db_profile_id=db_row["db_profile_id"],
                database_name=db_row["database_name"],
                description=db_row["description"],
                tables=tables_details,
                created_at=db_row["created_at"],
                updated_at=db_row["updated_at"],
            )
        finally:
            if conn:
                conn.close()

    def delete_annotation_by_id(self, annotation_id: str) -> bool:
        """
        annotationId로 특정 어노테이션을 삭제합니다.
        ON DELETE CASCADE에 의해 하위 데이터도 모두 삭제됩니다.
        성공 시 True, 대상이 없으면 False를 반환합니다.
        실패 시 sqlite3.Error를 발생시킵니다.
        """
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM database_annotation WHERE id = ?", (annotation_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            if conn:
                conn.close()


annotation_repository = AnnotationRepository()
