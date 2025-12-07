from pydantic import BaseModel
from typing import Optional


class RoleBase(BaseModel):
    key: str
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    is_system: bool = False


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Role(RoleBase):
    id: int
    is_system: bool
    
    class Config:
        from_attributes = True

