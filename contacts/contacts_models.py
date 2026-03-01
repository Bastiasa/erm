from sqlalchemy import Integer, String, Column
from core.database import base
from users.users_model import User

class Contacts(base):
    __tablename__ = 'contacs'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=False, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(Integer, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False) # e.g, personal, architect, client, employed... etc.