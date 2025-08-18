import sqlite3

from app.core.utils import get_db_path
from app.schemas.annotation.db_model import (
    ColumnAnnotationInDB,
    ConstraintColumnInDB,
    DatabaseAnnotationInDB,
    IndexAnnotationInDB,
    IndexColumnInDB,
    TableAnnotationInDB,
    TableConstraintInDB,
)
from app.schemas.annotation.response_model import (
    ColumnAnnotationDetail,
    ConstraintDetail,
    FullAnnotationResponse,
    IndexDetail,
    TableAnnotationDetail,
)


class AnnotationRepository:
    """
    어노테이션 데이터에 대한 데이터베이스 CRUD 작업을 처리합니다.
    모든 메서드는 내부적으로 `sqlite3`를 사용하여 로컬 DB와 상호작용합니다.
    """

    def create_full_annotation(
        self,
        db_conn: sqlite3.Connection,
        db_annotation: DatabaseAnnotationInDB,
        table_annotations: list[TableAnnotationInDB],
        column_annotations: list[ColumnAnnotationInDB],
        constraint_annotations: list[TableConstraintInDB],
        constraint_column_annotations: list[ConstraintColumnInDB],
        index_annotations: list[IndexAnnotationInDB],
        index_column_annotations: list[IndexColumnInDB],
    ) -> None:
        """
        하나의 트랜잭션 내에서 전체 어노테이션 데이터를 저장합니다.
        - 서비스 계층에서 트랜잭션을 관리하므로 connection을 인자로 받습니다.
        - 실패 시 sqlite3.Error를 발생시킵니다.
        """
        cursor = db_conn.cursor()

        # Database, Table, Column Annotations 저장
        db_data = (
            db_annotation.id,
            db_annotation.db_profile_id,
            db_annotation.database_name,
            db_annotation.description,
            db_annotation.created_at,
            db_annotation.updated_at,
        )
        cursor.execute(
            """
            INSERT INTO database_annotation (id, db_profile_id, database_name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            db_data,
        )
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

        # Constraint Annotations 저장
        constraint_data = [
            (
                c.id,
                c.table_annotation_id,
                c.constraint_type,
                c.name,
                c.description,
                c.expression,
                c.ref_table,
                c.on_update_action,
                c.on_delete_action,
                c.created_at,
                c.updated_at,
            )
            for c in constraint_annotations
        ]
        cursor.executemany(
            """
            INSERT INTO table_constraint (id, table_annotation_id, constraint_type, name, description, expression, ref_table, on_update_action, on_delete_action, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            constraint_data,
        )
        constraint_column_data = [
            (
                cc.id,
                cc.constraint_id,
                cc.column_annotation_id,
                cc.position,
                cc.referenced_column_name,
                cc.created_at,
                cc.updated_at,
            )
            for cc in constraint_column_annotations
        ]
        cursor.executemany(
            """
            INSERT INTO constraint_column (id, constraint_id, column_annotation_id, position, referenced_column_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            constraint_column_data,
        )

        # Index Annotations 저장
        index_data = [
            (i.id, i.table_annotation_id, i.name, i.is_unique, i.created_at, i.updated_at) for i in index_annotations
        ]
        cursor.executemany(
            """
            INSERT INTO index_annotation (id, table_annotation_id, name, is_unique, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            index_data,
        )
        index_column_data = [
            (ic.id, ic.index_id, ic.column_annotation_id, ic.position, ic.created_at, ic.updated_at)
            for ic in index_column_annotations
        ]
        cursor.executemany(
            """
            INSERT INTO index_column (id, index_id, column_annotation_id, position, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            index_column_data,
        )

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

            cursor.execute("SELECT * FROM database_annotation WHERE id = ?", (annotation_id,))
            db_row = cursor.fetchone()
            if not db_row:
                return None

            cursor.execute("SELECT * FROM table_annotation WHERE database_annotation_id = ?", (annotation_id,))
            table_rows = cursor.fetchall()

            tables_details = []
            for table_row in table_rows:
                table_id = table_row["id"]

                # 컬럼 정보
                cursor.execute(
                    "SELECT id, column_name, description, data_type, is_nullable, default_value FROM column_annotation WHERE table_annotation_id = ?",
                    (table_id,),
                )
                columns = []
                for c in cursor.fetchall():
                    c_dict = dict(c)
                    c_dict["is_nullable"] = (
                        bool(c_dict["is_nullable"]) if c_dict.get("is_nullable") is not None else None
                    )
                    columns.append(ColumnAnnotationDetail.model_validate(c_dict))

                # 제약조건 정보
                cursor.execute(
                    """
                    SELECT tc.name, tc.constraint_type, tc.description, ca.column_name
                    FROM table_constraint tc
                    LEFT JOIN constraint_column cc ON tc.id = cc.constraint_id
                    LEFT JOIN column_annotation ca ON cc.column_annotation_id = ca.id
                    WHERE tc.table_annotation_id = ?
                    """,
                    (table_id,),
                )
                constraint_map = {}
                for row in cursor.fetchall():
                    if row["name"] not in constraint_map:
                        constraint_map[row["name"]] = {
                            "type": row["constraint_type"],
                            "columns": [],
                            "description": row["description"],
                        }
                    if row["column_name"]:
                        constraint_map[row["name"]]["columns"].append(row["column_name"])
                constraints = [
                    ConstraintDetail(name=k, type=v["type"], columns=v["columns"], description=v["description"])
                    for k, v in constraint_map.items()
                ]

                # 인덱스 정보
                cursor.execute(
                    """
                    SELECT ia.name, ia.is_unique, ca.column_name
                    FROM index_annotation ia
                    JOIN index_column ic ON ia.id = ic.index_id
                    JOIN column_annotation ca ON ic.column_annotation_id = ca.id
                    WHERE ia.table_annotation_id = ?
                    """,
                    (table_id,),
                )
                index_map = {}
                for row in cursor.fetchall():
                    if row["name"] not in index_map:
                        index_map[row["name"]] = {"is_unique": bool(row["is_unique"]), "columns": []}
                    index_map[row["name"]]["columns"].append(row["column_name"])
                indexes = [
                    IndexDetail(name=k, is_unique=v["is_unique"], columns=v["columns"]) for k, v in index_map.items()
                ]

                tables_details.append(
                    TableAnnotationDetail(
                        id=table_id,
                        table_name=table_row["table_name"],
                        description=table_row["description"],
                        created_at=table_row["created_at"],
                        updated_at=table_row["updated_at"],
                        columns=columns,
                        constraints=constraints,
                        indexes=indexes,
                    )
                )

            db_row_dict = dict(db_row)
            db_row_dict["tables"] = tables_details
            return FullAnnotationResponse.model_validate(db_row_dict)
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
