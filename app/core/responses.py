from typing import Optional, List, TypeVar, Generic
from fastapi import status

from app.schemas.response import (
    BaseResponse,
    CreateResponse,
    UpdateResponse,
    GetResponse,
    ListResponse,
    ErrorDetail,
    MetaPagination
)
from app.core.pagination import get_pagination_meta

T = TypeVar('T')


def create_response(
    data: T,
    message: str = "Resource created successfully",
    status_code: int = status.HTTP_201_CREATED,
    errors: Optional[List[ErrorDetail]] = None
) -> CreateResponse[T]:
    """Cria uma resposta padronizada para criação de recursos"""
    return CreateResponse[T](
        message=message,
        status=status_code,
        result=data,
        errors=errors
    )


def update_response(
    data: T,
    message: str = "Resource updated successfully",
    status_code: int = status.HTTP_200_OK,
    errors: Optional[List[ErrorDetail]] = None
) -> UpdateResponse[T]:
    """Cria uma resposta padronizada para atualização de recursos"""
    return UpdateResponse[T](
        message=message,
        status=status_code,
        result=data,
        errors=errors
    )


def get_response(
    data: T,
    message: str = "Resource retrieved successfully",
    status_code: int = status.HTTP_200_OK,
    errors: Optional[List[ErrorDetail]] = None
) -> GetResponse[T]:
    """Cria uma resposta padronizada para busca de um único recurso"""
    return GetResponse[T](
        message=message,
        status=status_code,
        result=data,
        errors=errors
    )


def list_response(
    items: List[T],
    total: int,
    page: int,
    per_page: int,
    message: str = "Resources retrieved successfully",
    status_code: int = status.HTTP_200_OK,
    errors: Optional[List[ErrorDetail]] = None
) -> ListResponse[T]:
    """Cria uma resposta padronizada para listagem paginada"""
    meta = MetaPagination(**get_pagination_meta(total, page, per_page))
    
    return ListResponse[T](
        message=message,
        status=status_code,
        result=items,
        meta=meta,
        errors=errors
    )


def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: Optional[List[ErrorDetail]] = None
) -> BaseResponse[None]:
    """Cria uma resposta padronizada de erro"""
    return BaseResponse[None](
        message=message,
        status=status_code,
        result=None,
        errors=errors or []
    )


def error_detail(field: Optional[str] = None, message: str = "") -> ErrorDetail:
    """Cria um detalhe de erro"""
    return ErrorDetail(field=field, message=message)


def delete_response(
    message: str = "Resource deleted successfully",
    status_code: int = status.HTTP_200_OK,
    errors: Optional[List[ErrorDetail]] = None
):
    """Cria uma resposta padronizada para exclusão de recursos"""
    from app.schemas.response import DeleteResponse
    return DeleteResponse(
        message=message,
        status=status_code,
        result=None,
        errors=errors or []
    )


