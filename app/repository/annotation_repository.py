import logging
import sqlite3

from app.core.exceptions import APIException
from app.core.status import CommonCode
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
from app.schemas.annotation.hierarchical_response_model import (
    HierarchicalColumnAnnotation,
    HierarchicalDBAnnotation,
    HierarchicalDBMSAnnotation,
    HierarchicalRelationshipAnnotation,
    HierarchicalTableAnnotation,
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
                c.constraint_type.value,
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

    def update_db_profile_annotation_id(
        self, db_conn: sqlite3.Connection, db_profile_id: str, annotation_id: str
    ) -> None:
        """
        주어진 db_profile_id에 해당하는 레코드의 annotation_id를 업데이트합니다.
        - 서비스 계층에서 트랜잭션을 관리하므로 connection을 인자로 받습니다.
        - 실패 시 sqlite3.Error를 발생시킵니다.
        """
        cursor = db_conn.cursor()
        cursor.execute(
            "UPDATE db_profile SET annotation_id = ? WHERE id = ?",
            (annotation_id, db_profile_id),
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

    def find_hierarchical_annotation_by_profile_id(self, db_profile_id: str) -> HierarchicalDBMSAnnotation | None:
        """
        db_profile_id로 계층적 어노테이션 정보를 조회합니다.
        - DBMS > DB > 테이블 > 컬럼 구조로 데이터를 조립하여 반환합니다.
        """
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 1. 기본 정보 조회 (db_profile, database_annotation)
            cursor.execute(
                """
                SELECT
                    dp.type as dbms_type,
                    da.id as annotation_id,
                    da.db_profile_id,
                    da.database_name,
                    da.description as db_description,
                    da.created_at,
                    da.updated_at
                FROM db_profile dp
                JOIN database_annotation da ON dp.annotation_id = da.id
                WHERE dp.id = ?
                """,
                (db_profile_id,),
            )
            base_info = cursor.fetchone()
            if not base_info:
                return None

            # 2. 테이블 및 컬럼 정보 한번에 조회
            cursor.execute(
                """
                SELECT
                    ta.id as table_id,
                    ta.table_name,
                    ta.description as table_description,
                    ca.column_name,
                    ca.description as column_description,
                    ca.data_type
                FROM table_annotation ta
                JOIN column_annotation ca ON ta.id = ca.table_annotation_id
                WHERE ta.database_annotation_id = ?
                ORDER BY ta.table_name, ca.ordinal_position
                """,
                (base_info["annotation_id"],),
            )
            rows = cursor.fetchall()

            # 3. 데이터 계층 구조로 조립 (테이블, 컬럼)
            tables_map = {}
            for row in rows:
                table_name = row["table_name"]
                if table_name not in tables_map:
                    tables_map[table_name] = HierarchicalTableAnnotation(
                        table_name=table_name,
                        description=row["table_description"],
                        columns=[],
                    )
                tables_map[table_name].columns.append(
                    HierarchicalColumnAnnotation(
                        column_name=row["column_name"],
                        description=row["column_description"],
                        data_type=row["data_type"],
                    )
                )

            # 4. 관계 정보 조회
            cursor.execute(
                """
                SELECT
                    ta_from.table_name as from_table,
                    ca_from.column_name as from_column,
                    tc.ref_table as to_table,
                    cc.referenced_column_name as to_column,
                    tc.name as constraint_name,
                    tc.description as relationship_description
                FROM table_constraint tc
                JOIN table_annotation ta_from ON tc.table_annotation_id = ta_from.id
                JOIN constraint_column cc ON tc.id = cc.constraint_id
                JOIN column_annotation ca_from ON cc.column_annotation_id = ca_from.id
                WHERE ta_from.database_annotation_id = ? AND tc.constraint_type = 'FOREIGN KEY'
                ORDER BY tc.name, cc.position
                """,
                (base_info["annotation_id"],),
            )
            relationship_rows = cursor.fetchall()
            logging.info(f"Raw relationship rows from DB: {[dict(row) for row in relationship_rows]}")

            relationships_map = {}
            for row in relationship_rows:
                constraint_name = row["constraint_name"]
                if constraint_name not in relationships_map:
                    relationships_map[constraint_name] = {
                        "from_table": row["from_table"],
                        "to_table": row["to_table"],
                        "description": row["relationship_description"],
                        "from_columns": [],
                        "to_columns": [],
                    }
                relationships_map[constraint_name]["from_columns"].append(row["from_column"])
                relationships_map[constraint_name]["to_columns"].append(row["to_column"])

            logging.info(f"Processed relationships map: {relationships_map}")
            relationships = [HierarchicalRelationshipAnnotation(**data) for data in relationships_map.values()]
            logging.info(f"Final relationships list: {relationships}")

            # 5. 최종 데이터 조립
            db = HierarchicalDBAnnotation(
                db_name=base_info["database_name"],
                description=base_info["db_description"],
                tables=list(tables_map.values()),
                relationships=relationships,
            )

            return HierarchicalDBMSAnnotation(
                dbms_type=base_info["dbms_type"],
                databases=[db],
                annotation_id=base_info["annotation_id"],
                db_profile_id=base_info["db_profile_id"],
                created_at=base_info["created_at"],
                updated_at=base_info["updated_at"],
            )

        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL_FIND_ANNOTATION) from e
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
