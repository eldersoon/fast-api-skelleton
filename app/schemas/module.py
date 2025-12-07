from pydantic import BaseModel
from typing import Optional


class ModuleBase(BaseModel):
    key: str
    name: str
    description: Optional[str] = None


class Module(ModuleBase):
    id: int
    
    class Config:
        from_attributes = True

