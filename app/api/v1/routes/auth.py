from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import User
from app.schemas.response import GetResponse
from app.models.user import User as UserModel
from app.services.user_service import authenticate_user
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings
from app.core.responses import get_response

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    """Obtém o usuário atual através do token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    from app.services.user_service import get_user_by_email_or_username
    from sqlalchemy.orm import joinedload
    user = db.query(UserModel).options(
        joinedload(UserModel.role)
    ).filter(
        (UserModel.email == username) | (UserModel.username == username)
    ).first()
    
    if user is None:
        raise credentials_exception
    
    # Verificar se usuário tem permissão para acessar o sistema
    if not user.can_access_system or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user does not have permission to access the system."
        )
    
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Endpoint de login usando JSON (para uso geral/Insomnia)"""
    from app.services.user_service import get_user_by_email_or_username
    
    # Primeiro verificar se usuário existe e credenciais estão corretas
    user = get_user_by_email_or_username(db, login_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    from app.core.security import verify_password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Verificar se usuário tem permissão para acessar o sistema
    if not user.can_access_system or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user does not have permission to access the system."
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Endpoint de login usando OAuth2PasswordRequestForm (compatível com Swagger UI)"""
    from app.services.user_service import get_user_by_email_or_username
    
    # Primeiro verificar se usuário existe e credenciais estão corretas
    user = get_user_by_email_or_username(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    from app.core.security import verify_password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Verificar se usuário tem permissão para acessar o sistema
    if not user.can_access_system or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user does not have permission to access the system."
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=GetResponse[User])
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """Retorna informações do usuário atual"""
    return get_response(
        data=current_user,
        message="User retrieved successfully"
    )

