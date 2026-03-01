from core.security import Session
from contacts.contacts_models import Contacts
from sqlalchemy import or_

def build_query(session: Session, q: str | None, contact_type: str | None):
    query = session.query(Contacts)

    if q:
        query = query.filter(
            or_(
                Contacts.name.ilike(f"%{q}%"),
                Contacts.email.ilike(f"%{q}%"),
                Contacts.phone.ilike(f"%{q}%"),
                Contacts.contact_type.ilike(f"%{q}%")
            )
        )

    if contact_type:
        query = query.filter(Contacts.contact_type == contact_type)

    return query.order_by(Contacts.created_at.desc())