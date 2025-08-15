from fastapi import APIRouter, Depends

from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.annotation.request_model import AnnotationCreateRequest
from app.schemas.annotation.response_model import AnnotationDeleteResponse, FullAnnotationResponse
from app.services.annotation_service import AnnotationService, annotation_service

annotation_service_dependency = Depends(lambda: annotation_service)

router = APIRouter()


@router.post(
    "/create",
    response_model=ResponseMessage[FullAnnotationResponse],
    summary="새로운 어노테이션 생성",
)
async def create_annotation(
    request: AnnotationCreateRequest,
    service: AnnotationService = annotation_service_dependency,
) -> ResponseMessage[FullAnnotationResponse]:
    """
    `db_profile_id`를 받아 AI를 통해 DB 스키마를 분석하고 어노테이션을 생성하여 반환합니다.
    """
    new_annotation = await service.create_annotation(request)
    return ResponseMessage.success(value=new_annotation, code=CommonCode.SUCCESS_CREATE_ANNOTATION)


@router.get(
    "/find/{annotation_id}",
    response_model=ResponseMessage[FullAnnotationResponse],
    summary="특정 어노테이션 상세 정보 조회",
)
def get_annotation(
    annotation_id: str,
    service: AnnotationService = annotation_service_dependency,
) -> ResponseMessage[FullAnnotationResponse]:
    """
    `annotation_id`에 해당하는 어노테이션의 전체 상세 정보를 조회합니다.
    """
    annotation = service.get_full_annotation(annotation_id)
    return ResponseMessage.success(value=annotation, code=CommonCode.SUCCESS_FIND_ANNOTATION)


@router.get(
    "/find/db/{db_profile_id}",
    response_model=ResponseMessage[FullAnnotationResponse],
    summary="DB 프로필 ID로 어노테이션 조회",
)
def get_annotation_by_db_profile_id(
    db_profile_id: str,
    service: AnnotationService = annotation_service_dependency,
) -> ResponseMessage[FullAnnotationResponse]:
    """
    `db_profile_id`에 연결된 어노테이션의 전체 상세 정보를 조회합니다.
    """
    annotation = service.get_annotation_by_db_profile_id(db_profile_id)
    return ResponseMessage.success(value=annotation, code=CommonCode.SUCCESS_FIND_ANNOTATION)


@router.delete(
    "/remove/{annotation_id}",
    response_model=ResponseMessage[AnnotationDeleteResponse],
    summary="특정 어노테이션 삭제",
)
def delete_annotation(
    annotation_id: str,
    service: AnnotationService = annotation_service_dependency,
) -> ResponseMessage[AnnotationDeleteResponse]:
    """
    `annotation_id`에 해당하는 어노테이션 및 하위 데이터를 모두 삭제합니다.
    """
    result = service.delete_annotation(annotation_id)
    return ResponseMessage.success(value=result, code=CommonCode.SUCCESS_DELETE_ANNOTATION)
