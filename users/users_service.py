from sqlalchemy.orm import Session
from sqlalchemy import or_
from users.users_model import User
from core.security import bcrypt_context
import random
from datetime import datetime, timedelta
from core.email_service import send_verification_email
from core.config import VERIFICATION_TOKEN_EXPIRE_MINUTES
from users.users_model import Contacts

def authuser(identifier: str, password: str, db: Session):
    """Busca usuario por username O email, y verifica contraseña."""
    user = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    if not user:
        return None

    if not bcrypt_context.verify(password, user.password):
        return None

    return user

async def generate_and_send_verification_code(user: User, db: Session):
    code = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES)
    user.verification_code = code
    user.verification_code_expires_at = expires_at
    db.add(user)
    db.commit()
    db.refresh(user)
    await send_verification_email(user.email, code)
    return user

def verify_user_email(user: User, code: str, db: Session):
    if not user.verification_code or user.verification_code != code:
        return False
    if user.verification_code_expires_at < datetime.utcnow():
        return False
    user.is_verified = 1
    user.verification_code = None
    user.verification_code_expires_at = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return True

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