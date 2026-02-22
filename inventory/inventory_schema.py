from pydantic import BaseModel, Field
from datetime import date


class InventoryBase(BaseModel):
    item_name: str
    quantity: int
    description: str = Field(..., max_length=255) #descripcion no puede ser mayor a 255 caracteres

    class Config:
        from_attributes = True

class ItemCreate(InventoryBase):
    owner_id: int

    class Config:
        from_attributes = True

class ItemRead(BaseModel):
    id: int

    class Config:
        from_attributes = True

class InvLog(BaseModel):
    inventory_id: int
    user_id: int
    action: str 
    timestamp: date