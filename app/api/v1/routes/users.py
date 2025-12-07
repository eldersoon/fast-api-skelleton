from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.response import CreateResponse, GetResponse, ListResponse, UpdateResponse
from app.core.pagination import PaginationParams
from app.core.responses import (
    create_response,
    get_response,
    list_response,
    update_response,
    error_response,
    error_detail
)
from app.services.user_service import (
    get_user,
    get_users,
    create_user,
    update_user,
    get_user_by_email,
    get_user_by_username,
)
from app.api.v1.routes.auth import get_current_user
from app.models.user import User as UserModel

router = APIRouter()


@router.post("/", response_model=CreateResponse[User], status_code=status.HTTP_201_CREATED)
def create_user_route(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo usuário"""
    # Verifica se email já existe
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        return error_response(
            message="Validation error",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=[error_detail(field="email", message="Email already registered")]
        )
    
    # Verifica se username já existe
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        return error_response(
            message="Validation error",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=[error_detail(field="username", message="Username already registered")]
        )
    
    new_user = create_user(db=db, user=user)
    return create_response(
        data=new_user,
        message="User created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.get("/", response_model=ListResponse[User])
def read_users(
    pagination: PaginationParams = Depends(),
    email: Optional[str] = None,
    username: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Lista todos os usuários com paginação e filtros (requer autenticação)"""
    users, total = get_users(
        db,
        page=pagination.page,
        per_page=pagination.perPage,
        email=email,
        username=username,
        is_active=is_active
    )
    
    return list_response(
        items=users,
        total=total,
        page=pagination.page,
        per_page=pagination.perPage,
        message="Users retrieved successfully"
    )


@router.get("/{user_id}", response_model=GetResponse[User])
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Busca um usuário por ID (requer autenticação)"""
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        return error_response(
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
            errors=[error_detail(message=f"User with ID {user_id} not found")]
        )
    
    return get_response(
        data=db_user,
        message="User retrieved successfully"
    )


@router.put("/{user_id}", response_model=UpdateResponse[User])
def update_user_route(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Atualiza um usuário (requer autenticação)"""
    # Só pode atualizar se for o próprio usuário ou se for superuser
    if current_user.id != user_id and not current_user.is_superuser:
        return error_response(
            message="Not enough permissions",
            status_code=status.HTTP_403_FORBIDDEN,
            errors=[error_detail(message="You can only update your own profile")]
        )
    
    db_user = update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        return error_response(
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
            errors=[error_detail(message=f"User with ID {user_id} not found")]
        )
    
    return update_response(
        data=db_user,
        message="User updated successfully"
    )

