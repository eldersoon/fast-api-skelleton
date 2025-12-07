from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class ErrorDetail(BaseModel):
    """Detalhe de um erro"""
    field: Optional[str] = None
    message: str


class MetaPagination(BaseModel):
    """Metadados de paginação"""
    total: int = Field(..., description="Total de itens")
    page: int = Field(..., description="Página atual")
    perPage: int = Field(..., description="Itens por página")
    totalPages: int = Field(..., description="Total de páginas")
    hasNext: bool = Field(..., description="Tem próxima página")
    hasPrevious: bool = Field(..., description="Tem página anterior")


class BaseResponse(BaseModel, Generic[T]):
    """Resposta base padronizada"""
    message: str = Field(..., description="Mensagem descritiva da resposta")
    status: int = Field(..., description="Código de status HTTP")
    result: Optional[T] = Field(None, description="Dados da resposta")
    errors: Optional[List[ErrorDetail]] = Field(None, description="Lista de erros, se houver")


class CreateResponse(BaseResponse[T], Generic[T]):
    """Resposta para criação de recursos"""
    pass


class UpdateResponse(BaseResponse[T], Generic[T]):
    """Resposta para atualização de recursos"""
    pass


class GetResponse(BaseResponse[T], Generic[T]):
    """Resposta para busca de um único recurso"""
    pass


class ListResponse(BaseResponse[List[T]], Generic[T]):
    """Resposta para listagem paginada de recursos"""
    meta: Optional[MetaPagination] = Field(None, description="Metadados de paginação")


