from fastapi import HTTPException, status
from contacts.contacts_models import Contacts
from sqlalchemy.orm import Session
from contacts.contacts_schema import ContactsBase
from users.users_model import User

def CreateContact(ctccreate: ContactsBase, user: User, session: Session):
    
    new_contact = Contacts(
        name = ctccreate.name,
        email = ctccreate.email,
        phone = ctccreate.phone,
        type = ctccreate.type
    )

    contact = session.query(Contacts).filter((Contacts.email == ctccreate.email) | (Contacts.name == ctccreate.name) | (Contacts.phone == ctccreate.phone)).first()

    if contact:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User alredy exist")

    if not user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not authenticated")
    
    session.add(new_contact)
    session.commit()
    session.refresh(new_contact)
    
    return new_contact