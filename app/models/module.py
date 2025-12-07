from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Module(Base):
    """Model de módulo do sistema"""
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    
    # Relacionamentos
    permissions = relationship("RoleModulePermission", back_populates="module", cascade="all, delete-orphan")

