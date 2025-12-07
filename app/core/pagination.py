from typing import Optional
from pydantic import BaseModel, Field, field_validator
from math import ceil


class PaginationParams(BaseModel):
    """Parâmetros de paginação"""
    page: int = Field(default=1, ge=1, description="Número da página (começa em 1)")
    perPage: int = Field(default=10, ge=1, le=100, description="Itens por página (máximo 100)")
    
    @field_validator('page')
    @classmethod
    def validate_page(cls, v: int) -> int:
        if v < 1:
            return 1
        return v
    
    @field_validator('perPage')
    @classmethod
    def validate_per_page(cls, v: int) -> int:
        if v < 1:
            return 10
        if v > 100:
            return 100
        return v
    
    @property
    def skip(self) -> int:
        """Calcula o offset para SQL (skip)"""
        return (self.page - 1) * self.perPage
    
    @property
    def limit(self) -> int:
        """Retorna o limite (perPage)"""
        return self.perPage


def get_pagination_meta(total: int, page: int, per_page: int) -> dict:
    """
    Calcula os metadados de paginação
    
    Args:
        total: Total de itens
        page: Página atual
        per_page: Itens por página
    
    Returns:
        Dicionário com metadados de paginação
    """
    total_pages = ceil(total / per_page) if total > 0 else 0
    
    return {
        "total": total,
        "page": page,
        "perPage": per_page,
        "totalPages": total_pages,
        "hasNext": page < total_pages,
        "hasPrevious": page > 1
    }


