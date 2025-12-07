from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha plain corresponde ao hash"""
    try:
        # Garantir que plain_password seja uma string e bytes
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        
        # Garantir que hashed_password seja bytes
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Gera o hash da senha usando bcrypt"""
    # Garantir que a senha seja uma string
    if not isinstance(password, str):
        password = str(password)
    
    # Converter para bytes
    password_bytes = password.encode('utf-8')
    
    # Bcrypt tem limite de 72 bytes para a senha
    # Truncar se necessário (muito raro, mas seguro)
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Gerar salt e hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Retornar como string
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica um token JWT"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

