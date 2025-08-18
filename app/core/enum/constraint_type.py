from enum import Enum


class ConstraintTypeEnum(str, Enum):
    """
    데이터베이스 제약 조건의 유형을 정의하는 Enum 클래스입니다.
    - str을 상속하여 Enum 멤버를 문자열 값처럼 사용할 수 있습니다.
    """

    PRIMARY_KEY = "PRIMARY KEY"
    FOREIGN_KEY = "FOREIGN KEY"
    UNIQUE = "UNIQUE"
    CHECK = "CHECK"
    NOT_NULL = "NOT NULL"  # 일부 DB에서는 제약조건으로 취급
    DEFAULT = "DEFAULT"  # 일부 DB에서는 제약조건으로 취급
    INDEX = "INDEX"  # 제약조건은 아니지만, 관련 정보로 포함
