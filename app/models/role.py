from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class Role(Base):
    """Model de papel/role de acesso"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)
    
    # Relacionamentos
    users = relationship("User", back_populates="role")
    permissions = relationship("RoleModulePermission", back_populates="role", cascade="all, delete-orphan")

