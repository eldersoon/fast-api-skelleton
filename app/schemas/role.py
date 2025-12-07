from pydantic import BaseModel
from typing import Optional


class RoleBase(BaseModel):
    key: str
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    # is_system sempre será False para roles criadas via API
    pass


class RoleUpdate(BaseModel):
    key: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class Role(RoleBase):
    id: int
    is_system: bool
    
    class Config:
        from_attributes = True

