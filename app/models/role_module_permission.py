from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class RoleModulePermission(Base):
    """Model de permissão de role em módulo"""
    __tablename__ = "role_module_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    can_read = Column(Boolean, default=False, nullable=False)
    can_create = Column(Boolean, default=False, nullable=False)
    can_update = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)
    
    # Relacionamentos
    role = relationship("Role", back_populates="permissions")
    module = relationship("Module", back_populates="permissions")
    
    # Constraint único: uma role só pode ter uma permissão por módulo
    __table_args__ = (
        UniqueConstraint('role_id', 'module_id', name='uq_role_module'),
    )

