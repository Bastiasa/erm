from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from users.users_model import User, Contacts
from core.security import bcrypt_context, verify_token
from core.dependencies import CreateSession
from users.users_service import build_query
from core.dependencies import templates

contacts_router = APIRouter(prefix="/ctc", tags=["ctc"])

@contacts_router.post("/contacts")
def create_contact(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    contact_type: str = Form(...),
    address: str = Form(...),
    session: Session = Depends(CreateSession)
):
    contact = Contacts(
        name=name,
        email=email,
        phone=phone,
        contact_type=contact_type,
        address=address
    )

    session.add(contact)
    session.commit()

    return RedirectResponse(url="/home/contacts", status_code=303)




#VIEWS

@contacts_router.get("/contacts")
def get_contacts(
    request: Request,
    q: str | None = None,
    contact_type: str | None = None,
    session: Session = Depends(CreateSession)
):
    contacts = build_query(session, q, contact_type).all()

    return templates.TemplateResponse(
        "contacts/contacts.html",
        {
            "request": request,
            "contacts": contacts,
            "q": q,
            "contact_type": contact_type
        }
    )