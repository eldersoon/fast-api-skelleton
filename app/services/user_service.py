from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> User | None:
    """Busca um usuário por ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Busca um usuário por email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Busca um usuário por username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email_or_username(db: Session, identifier: str) -> User | None:
    """Busca um usuário por email ou username"""
    return db.query(User).filter(
        or_(User.email == identifier, User.username == identifier)
    ).first()


def count_users(
    db: Session,
    email: Optional[str] = None,
    username: Optional[str] = None,
    is_active: Optional[bool] = None
) -> int:
    """Conta o total de usuários com filtros aplicados"""
    query = db.query(func.count(User.id))
    
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.scalar()


def get_users(
    db: Session,
    page: int = 1,
    per_page: int = 10,
    email: Optional[str] = None,
    username: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Tuple[List[User], int]:
    """
    Lista usuários com paginação e filtros
    
    Args:
        db: Sessão do banco de dados
        page: Número da página (começa em 1)
        per_page: Itens por página
        email: Filtrar por email (busca parcial, case-insensitive)
        username: Filtrar por username (busca parcial, case-insensitive)
        is_active: Filtrar por status ativo
    
    Returns:
        Tupla (lista de usuários, total de registros)
    """
    query = db.query(User)
    
    # Aplicar filtros
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Contar total antes da paginação
    total = query.count()
    
    # Aplicar paginação
    skip = (page - 1) * per_page
    users = query.offset(skip).limit(per_page).all()
    
    return users, total


def create_user(db: Session, user: UserCreate) -> User:
    """Cria um novo usuário"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=user.is_active,
        can_access_system=user.can_access_system,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User | None:
    """Atualiza um usuário"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Se houver senha, fazer hash
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Autentica um usuário.
    
    Verifica credenciais e permissão de acesso ao sistema.
    Retorna None se credenciais inválidas ou se usuário não tem permissão.
    """
    user = get_user_by_email_or_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    # Bloquear acesso se usuário não tem permissão ou está inativo
    if not user.can_access_system or not user.is_active:
        return None
    
    return user

