from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class types(str, Enum):
    architect = 'architect'
    personal = 'personal'
    employed = 'employed'
    client = 'client'


class ContactsBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: str
    type: types