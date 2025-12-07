from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.responses import error_response, error_detail


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler para HTTPException - converte para formato padronizado"""
    status_code = exc.status_code
    detail = exc.detail
    
    # Se detail for uma string simples
    if isinstance(detail, str):
        errors = [error_detail(message=detail)]
    else:
        errors = [error_detail(message=str(detail))]
    
    response = error_response(
        message=detail if isinstance(detail, str) else "An error occurred",
        status_code=status_code,
        errors=errors
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler para erros de validação do Pydantic"""
    errors = []
    
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "Validation error")
        errors.append(error_detail(field=field, message=message))
    
    response = error_response(
        message="Validation error",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.model_dump(exclude_none=True)
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler genérico para exceções não tratadas"""
    response = error_response(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors=[error_detail(message="An unexpected error occurred")]
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(exclude_none=True)
    )

