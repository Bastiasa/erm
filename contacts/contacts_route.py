from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from contacts.contacts_models import Contacts
from contacts.contacts_services import build_query
from core.dependencies import CreateSession
from core.dependencies import templates

contacts_router = APIRouter(prefix="/ctc", tags=["ctc"])

@contacts_router.post("/add")
def create_contact(name: str = Form(...), email: str = Form(...), phone: str = Form(...), contact_type: str = Form(...), address: str = Form(...), session: Session = Depends(CreateSession)):
    contact = Contacts(
        name=name,
        email=email,
        phone=phone,
        contact_type=contact_type,
        address=address
    )

    session.add(contact)
    session.commit()

    return RedirectResponse(url="/ctc", status_code=303)




#VIEWS

@contacts_router.get("/")
def get_contacts(request: Request, query: str | None = None, contact_type: str | None = None, session: Session = Depends(CreateSession)):
    contacts = build_query(session, query, contact_type).all()

    return templates.TemplateResponse(
        "contacts/contacts.html",
        {
            "request": request,
            "contacts": contacts,
            "query": query,
            "contact_type": contact_type
        }
    )